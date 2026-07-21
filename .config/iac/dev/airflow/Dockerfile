# Image Airflow custom pour piloter des jobs Spark via SparkSubmitOperator.
# La base apache/airflow n'embarque ni Java ni spark-submit : on les ajoute,
# car le driver Spark tourne dans le worker Airflow (deploy-mode=client).
ARG AIRFLOW_IMAGE_NAME=apache/airflow:2.10.1
FROM ${AIRFLOW_IMAGE_NAME}

USER root

# Java (requis par spark-submit) + procps (utilisé par certains scripts Spark)
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jdk procps \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# JAVA_HOME pointant vers l'installation par défaut (openjdk-17 sur bookworm)
ENV JAVA_HOME=/usr/lib/jvm/default-java

USER airflow

# Provider Spark d'Airflow + client PySpark (fournit spark-submit).
# pyspark DOIT matcher EXACTEMENT la version du cluster (bitnami/spark:3.5.6),
# sinon : java.io.InvalidClassException (serialVersionUID Task incompatible).
RUN pip install --no-cache-dir \
    "apache-airflow-providers-apache-spark==4.11.1" \
    "pyspark==3.5.6"
