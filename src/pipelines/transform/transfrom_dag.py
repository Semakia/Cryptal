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

    # ── ÉTAPE 1 : Construire crypto_prices_series (bronze → silver)
    build_price_series = SparkSubmitOperator(
        task_id="build_price_series",
        conn_id="spark_default",
        application=f"{SCRIPTS_PATH}/pipelines/transform/utils/price_series_builder.py",
        packages="org.postgresql:postgresql:42.6.0",
        conf={
            "spark.master": SPARK_MASTER,
            "spark.executor.memory": "1g",
            "spark.driver.memory": "512m",
        },
        env_vars={
            "BRONZE_DB_HOST": "91.134.132.149",
            "BRONZE_DB_PORT": "5432",
            "BRONZE_DB_NAME": "crypto_viz_bronze",
            "BRONZE_DB_USER": "cryptoviz",
            "BRONZE_DB_PASSWORD": "{{ var.value.bronze_db_password }}",
            "SILVER_DB_HOST": "91.134.132.149",
            "SILVER_DB_PORT": "5432",
            "SILVER_DB_NAME": "crypto_viz_silver",
            "SILVER_DB_USER": "cryptoviz",
            "SILVER_DB_PASSWORD": "{{ var.value.silver_db_password }}",
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
            "SILVER_DB_HOST": "91.134.132.149",
            "SILVER_DB_PORT": "5432",
            "SILVER_DB_NAME": "crypto_viz_silver",
            "SILVER_DB_USER": "cryptoviz",
            "SILVER_DB_PASSWORD": "{{ var.value.silver_db_password }}",
        },
    )

    # Note : la volatilité (stddev) et la matrice de corrélation sont déjà
    # produites par run_transform (crypto_price_indicators +
    # crypto_correlation_matrix). Les métriques fines par crypto sont calculées
    # à la demande par l'API depuis crypto_prices_series.

    # ── Workflow
    (
        start
        >> build_price_series
        >> [run_transform]  # parallèle
        >> end
    )