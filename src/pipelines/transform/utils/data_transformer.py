from pyspark.sql import SparkSession
from pyspark.sql import functions as F
import pandas as pd

spark = SparkSession.builder.appName("CryptoDataTransformation").getOrCreate()


class CryptoDataTransformer:
    def __init__(self, spark: SparkSession):
        self.spark = spark

    def calculate_daily_average(
        self,
        input_dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate daily average prices for each cryptocurrency.

        Parameters
        ----------
        input_df : DataFrame
            The input DataFrame containing cryptocurrency price data.

        Returns
        -------
        DataFrame
            A DataFrame with daily average prices for each cryptocurrency.
        """

    def get_price_series(
        self,
        input_dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get price series for each cryptocurrency.

        Parameters
        ----------
        input_dataframe : DataFrame
            The input DataFrame containing cryptocurrency price data.

        Returns
        -------
        DataFrame
            A DataFrame with price series for each cryptocurrency.
        """
        cutoff = F.current_timestamp() - F.expr("INTERVAL 30 DAYS")

        dataframe_filtered = (
            input_dataframe
            .filter(F.col("price_usd").isNotNull())
            .filter(F.col("timestamp") >= cutoff)
        )
        dataframe_series = (
            dataframe_filtered
            .withColumn(
                "time_bucket",
                F.date_trunc("hour", F.col("timestamp"))
            )
            .groupBy("coin_id", "time_bucket")
            .agg(F.avg("price_usd").alias("price_usd"))
        )

        return dataframe_series

    def transform(
        self,
        input_dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Transform the input DataFrame by calculating daily average prices.

        Parameters
        ----------
        dataframe : DataFrame
            The input DataFrame containing cryptocurrency price data.

        Returns
        -------
        DataFrame
            A DataFrame with the transformed cryptocurrency price data.
        """
        data_transformed = self.get_price_series(input_dataframe)
        return data_transformed
