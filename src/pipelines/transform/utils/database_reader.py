from typing import Optional
from pyspark.sql import SparkSession
import pandas as pd

spark = (
    SparkSession
    .builder
    .appName("CryptoVizDataReader")
    .getOrCreate()
)


class CryptoDatabaseReader:
    """
    Utility class for interacting with a database via Spark.

    Parameters
    ----------
    spark : SparkSession
        The active Spark session to use for reading operations.
    """

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def read_from_db(
        self,
        jdbc_url: str,
        table_name: str,
        schema_name: str,
        properties: dict
    ) -> Optional[pd.DataFrame]:
        """
        This function Read data from a database table into a Spark DataFrame.
        Parameters
        ----------
        jdbc_url: str
            url of database connection
        table_name: str
            name of the table
        schema_name: str
            name of the schema
        properties: dict

        Returns
        -------
            Optional[Dataframe]
                The result of the reading of the table
        """

        dataframe = (
                self.spark.read.format("jdbc")
                .option("url", jdbc_url)
                .option("dbtable", f"{schema_name}.{table_name}")
                .option("user", properties["user"])
                .option("password", properties["password"])
                .option("driver", properties["driver"])
                .load()
        )

        return dataframe

    def load_to_db(
        self,
        dataframe: pd.DataFrame,
        jdbc_url: str,
        table_name: str,
        schema_name: str,
        properties: dict
    ) -> None:
        """
        This function writes a Spark DataFrame to a database table.

        Parameters
        ----------
        dataframe: DataFrame
            The DataFrame to write to the database.
        jdbc_url: str
            url of database connection
        table_name: str
            name of the table
        schema_name: str
            name of the schema
        properties: dict

        Returns
        -------
            None
        """

        (
            dataframe.write.format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", f"{schema_name}.{table_name}")
            .option("user", properties["user"])
            .option("password", properties["password"])
            .option("driver", properties["driver"])
            .mode("overwrite")
            .save()
        )
