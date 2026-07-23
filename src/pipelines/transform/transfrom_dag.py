from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
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
        jars=f"{SCRIPTS_PATH}/jars/postgresql-42.6.0.jar",
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
            # Fenêtre de lookback (jours). Grande valeur ici car la donnée
            # bronze de démo date de nov-déc 2025. En prod : ramener à ~30.
            "LOOKBACK_DAYS": "3650",
        },
    )

    # ── ÉTAPE 2a : Calcul des indicateurs (SMA, RSI, stddev)
    run_transform = SparkSubmitOperator(
        task_id="run_transform",
        conn_id="spark_default",
        application=f"{SCRIPTS_PATH}/pipelines/transform/transform.py",
        jars=f"{SCRIPTS_PATH}/jars/postgresql-42.6.0.jar",
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

    # ── ÉTAPE 3 : Couche GOLD (métriques pré-calculées qui nourrissent l'API)
    # Script psycopg2 (réutilise les calculateurs, lecture silver) -> BashOperator.
    # GOLD_PERIOD_DAYS=365 car la donnée démo date de nov-déc 2025 (~245j).
    # En prod avec données fraîches : ramener à 30.
    build_gold = BashOperator(
        task_id="build_gold",
        bash_command=(
            f"python {SCRIPTS_PATH}/pipelines/transform/build_gold.py"
        ),
        append_env=True,  # conserve PYTHONPATH (=/opt/spark/scripts) du conteneur
        env={
            "SILVER_DB_HOST": "91.134.132.149",
            "SILVER_DB_PORT": "5432",
            "SILVER_DB_NAME": "crypto_viz_silver",
            "SILVER_DB_USER": "cryptoviz",
            "SILVER_DB_PASSWORD": "{{ var.value.silver_db_password }}",
            "GOLD_DB_HOST": "91.134.132.149",
            "GOLD_DB_PORT": "5432",
            "GOLD_DB_NAME": "crypto_viz_gold",
            "GOLD_DB_USER": "cryptoviz",
            "GOLD_DB_PASSWORD": "{{ var.value.gold_db_password }}",
            "GOLD_PERIOD_DAYS": "365",
        },
    )

    # ── Workflow : bronze -> silver -> gold
    start >> build_price_series >> run_transform >> build_gold >> end