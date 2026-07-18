import os
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

# Paramètres de connexion à la base de données source (Bronze)
bronze_url = (
    f"jdbc:postgresql://{os.environ['BRONZE_DB_HOST']}:"
    f"{os.environ['BRONZE_DB_PORT']}/{os.environ['BRONZE_DB_NAME']}"
)
bronze_properties = {
    "user": os.getenv("BRONZE_DB_USER"),
    "password": os.getenv("BRONZE_DB_PASSWORD"),
    "driver": "org.postgresql.Driver"
}

# Paramètres de connexion à la base de données de destination (Silver)
silver_url = (
    f"jdbc:postgresql://{os.environ['SILVER_DB_HOST']}:"
    f"{os.environ['SILVER_DB_PORT']}/{os.environ['SILVER_DB_NAME']}"
)
silver_properties = {
    "user": os.getenv("SILVER_DB_USER"),
    "password": os.getenv("SILVER_DB_PASSWORD"),
    "driver": "org.postgresql.Driver"
}


def main():
    # Initialiser SparkSession
    spark = (
        SparkSession.builder
        .appName("PriceSeriesBuilder")
        .getOrCreate()
    )

    # Lire les données brutes depuis la table source
    dataframe_bronze = (
        spark.read.format("jdbc")
        .option("url", bronze_url)
        .option("dbtable", "public.crypto_prices")
        .options(**bronze_properties)
        .load()
    )

    # Filtrer les données des 30 derniers jours et calculer les buckets horaires
    cutoff = F.current_timestamp() - F.expr("INTERVAL 30 DAYS")

    dataframe_filtered = (
        dataframe_bronze
        .filter(F.col("price_usd").isNotNull())
        .filter(F.col("timestamp") >= cutoff)
    )

    # Agréger par coin_id et time_bucket (troncature à l'heure)
    dataframe_series = (
        dataframe_filtered
        .withColumn(
            "time_bucket",
            F.date_trunc("hour", F.col("timestamp"))
        )
        .groupBy("coin_id", "time_bucket")
        .agg(F.avg("price_usd").alias("price_usd"))
        .orderBy("coin_id", "time_bucket")
    )

    # Écrire le résultat dans la table de destination
    (
        dataframe_series.write
        .format("jdbc")
        .option("url", silver_url)
        .option("dbtable", "public.crypto_prices_series")
        .option("user", silver_properties["user"])
        .option("password", silver_properties["password"])
        .option("driver", "org.postgresql.Driver")
        .mode("overwrite")
        .save()
    )

    print(f"""crypto_prices_series rebuilt: {dataframe_series.count()}
           rows written.""")
    spark.stop()


if __name__ == "__main__":
    main()