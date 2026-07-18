from pyspark.sql import SparkSession
import os
from pipelines.transform.utils.data_transformer import CryptoDataTransformer
from pipelines.transform.utils.database_reader import CryptoDatabaseReader

spark_session = (
    SparkSession.builder
    .appName("CryptoDataApp")
    .getOrCreate()
)

database_reader = CryptoDatabaseReader(spark_session)
data_transformer = CryptoDataTransformer(spark_session)

# Source ET destination sont dans Silver : crypto_prices_series (construite
# par build_price_series) est enrichie en indicateurs puis réécrite dans Silver.
SRC_DB_NAME = os.getenv("SILVER_DB_NAME")
SRC_DB_PORT = os.getenv("SILVER_DB_PORT")
SRC_DB_HOST = os.getenv("SILVER_DB_HOST")
SRC_DB_USER = os.getenv("SILVER_DB_USER")
SRC_DB_PASSWORD = os.getenv("SILVER_DB_PASSWORD")

DEST_DB_NAME = os.getenv("SILVER_DB_NAME")
DEST_DB_USER = os.getenv("SILVER_DB_USER")
DEST_DB_PASSWORD = os.getenv("SILVER_DB_PASSWORD")
DEST_DB_HOST = os.getenv("SILVER_DB_HOST")
DEST_DB_PORT = os.getenv("SILVER_DB_PORT")

src_jdbc_url = f"jdbc:postgresql://{SRC_DB_HOST}:{SRC_DB_PORT}/{SRC_DB_NAME}"
src_table_name = "crypto_prices_series"
schema_name = "public"
src_db_props = {
    "user": SRC_DB_USER,
    "password": SRC_DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}

dest_table_name = "crypto_price_indicators"
dest_jdbc_url = f"jdbc:postgresql://{DEST_DB_HOST}:{DEST_DB_PORT}/{DEST_DB_NAME}"
dest_db_props = {
    "user": DEST_DB_USER,
    "password": DEST_DB_PASSWORD,
    "driver": "org.postgresql.Driver"
}


def main():
    # Étape 1 : lire depuis Bronze
    price_series_dataframe = database_reader.read_from_db(
        jdbc_url=src_jdbc_url,
        table_name=src_table_name,
        schema_name=schema_name,
        properties=src_db_props
    )
    print(f"Nombre de lignes lues depuis Bronze : {price_series_dataframe.count()}")
    price_series_dataframe.show(truncate=False)

    # Étape 2 : transformer (price_series + SMA + RSI + volatilité)
    transformed_df = data_transformer.transform(price_series_dataframe)
    print(f"Nombre de lignes après transformation : {transformed_df.count()}")
    transformed_df.show(truncate=False)

    # Étape 3 : écrire vers Silver
    database_reader.load_to_db(
        dataframe=transformed_df,
        jdbc_url=dest_jdbc_url,
        table_name=dest_table_name,
        schema_name=schema_name,
        properties=dest_db_props
    )
    print(f"Table {dest_table_name} écrite avec succès dans Silver DB")

    # Étape 4 (optionnel) : calcul de corrélation séparé
    correlation_df = data_transformer.calculate_correlation(
        price_series_dataframe, granularity="daily"
    )
    print("Corrélations entre paires de cryptos :")
    correlation_df.show(truncate=False)

    correlation_table = "crypto_correlation_matrix"
    database_reader.load_to_db(
        dataframe=correlation_df,
        jdbc_url=dest_jdbc_url,
        table_name=correlation_table,
        schema_name=schema_name,
        properties=dest_db_props
    )
    print(f"Table {correlation_table} écrite avec succès")

    spark_session.stop()


if __name__ == "__main__":
    main()