from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

SPARK_MASTER = "spark://spark-master:7077"
SCRIPTS_PATH = "/opt/spark/scripts"
PG_JAR       = "/opt/spark/jars/postgresql-42.6.0.jar"

default_args = {
    "owner": "cryptoviz",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

with DAG(
    dag_id="cryptoviz_pipeline",
    default_args=default_args,
    description="Pipeline complet CryptoViz : ingestion → silver → gold",
    schedule_interval="0 * * * *",   # toutes les heures
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["cryptoviz", "spark"],
) as dag:

    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    # ── ÉTAPE 1 : Construire crypto_price_series (bronze → silver)
    build_price_series = SparkSubmitOperator(
        task_id="build_price_series",
        conn_id="spark_default",
        application=f"{SCRIPTS_PATH}/pipelines/transform/build_price_series.py",
        packages="org.postgresql:postgresql:42.6.0",
        conf={
            "spark.master": SPARK_MASTER,
            "spark.executor.memory": "1g",
            "spark.driver.memory": "512m",
        },
        env_vars={
            "BRONZE_DB_HOST": "dev-bronze",
            "BRONZE_DB_PORT": "5432",
            "BRONZE_DB_NAME": "bronze_db",
            "BRONZE_DB_USER": "cryptoviz",
            "BRONZE_DB_PASSWORD": "{{ var.value.bronze_db_password }}",
            "SILVER_DB_HOST": "dev-silver",
            "SILVER_DB_NAME": "crypto_viz_silver",
        },
    )

    # ── ÉTAPE 2a : Calcul des indicateurs (SMA, RSI, stddev)
    run_transform = SparkSubmitOperator(
        task_id="run_transform",
        conn_id="spark_default",
        application=f"{SCRIPTS_PATH}/pipelines/transform/transform.py",
        packages="org.postgresql:postgresql:42.6.0",
        conf={
            "spark.master": SPARK_MASTER,
            "spark.executor.memory": "1g",
        },
        env_vars={
            "SILVER_DB_HOST": "dev-silver",
            "SILVER_DB_NAME": "crypto_viz_silver",
            "SILVER_DB_USER": "cryptoviz",
            "SILVER_DB_PASSWORD": "{{ var.value.silver_db_password }}",
        },
    )

    # ── ÉTAPE 2b : Calcul volatilité (silver → gold)
    run_volatility = SparkSubmitOperator(
        task_id="run_volatility",
        conn_id="spark_default",
        application=f"{SCRIPTS_PATH}/pipelines/analytics/volatility.py",
        packages="org.postgresql:postgresql:42.6.0",
        conf={"spark.master": SPARK_MASTER},
        env_vars={
            "SILVER_DB_HOST": "dev-silver",
            "SILVER_DB_NAME": "crypto_viz_silver",
            "SILVER_DB_USER": "cryptoviz",
            "SILVER_DB_PASSWORD": "{{ var.value.silver_db_password }}",
        },
    )

    # ── ÉTAPE 2c : Calcul corrélations (silver → gold)
    run_correlation = SparkSubmitOperator(
        task_id="run_correlation",
        conn_id="spark_default",
        application=f"{SCRIPTS_PATH}/pipelines/analytics/correlation.py",
        packages="org.postgresql:postgresql:42.6.0",
        conf={"spark.master": SPARK_MASTER},
        env_vars={
            "SILVER_DB_HOST": "dev-silver",
            "SILVER_DB_NAME": "crypto_viz_silver",
            "SILVER_DB_USER": "cryptoviz",
            "SILVER_DB_PASSWORD": "{{ var.value.silver_db_password }}",
        },
    )

    # ── Workflow
    (
        start
        >> build_price_series
        >> [run_transform, run_volatility, run_correlation]  # parallèle
        >> end
    )