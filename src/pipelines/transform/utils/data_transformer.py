from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import pandas as pd


class CryptoDataTransformer:
    def __init__(self, spark: SparkSession):
        self.spark = spark


    def calculate_volatility(
        self,
        price_series_df: DataFrame,
        granularity: str = "daily"
    ) -> DataFrame:
        """
        Calcule la volatilité (stddev) sur crypto_prices_series.
        granularity: "daily" → fenêtre de 24h, "hourly" → fenêtre de 1h
        Args:
            price_series_df: DataFrame avec colonnes coin_id, time_bucket, price_usd
            granularity: "daily" ou "hourly"
        """
        w = Window.partitionBy("coin_id").orderBy("time_bucket")

        if granularity == "daily":
            # Moyenne glissante sur 24 buckets (24h)
            avg_col = F.avg("price_usd").over(w.rowsBetween(-23, 0))
        else:  # hourly
            # Moyenne glissante sur 1 bucket
            avg_col = F.avg("price_usd").over(w.rowsBetween(0, 0))

        df_vol = (
            price_series_df
            .withColumn("avg_price", avg_col)
            .withColumn("volatility", F.stddev_pop("price_usd").over(w.rowsBetween(-23, 0) if granularity == "daily" else w.rowsBetween(0, 0)))
            .drop("avg_price")
        )
        return df_vol

    def calculate_sma(
        self,
        price_series_df: DataFrame,
        window_size: int = 20
    ) -> DataFrame:
        """
        Calcule la SMA (Simple Moving Average) sur crypto_prices_series.
        Args:
            price_series_df: DataFrame avec colonnes coin_id, time_bucket, price_usd
            window_size: nombre de buckets pour la moyenne (ex: 20 pour 20h)
        Return:
            DataFrame avec colonne sma_{window_size}
        """
        w = Window.partitionBy("coin_id").orderBy("time_bucket")
        df_sma = (
            price_series_df
            .withColumn(
                f"sma_{window_size}",
                F.avg("price_usd").over(w.rowsBetween(-window_size + 1, 0))
            )
        )
        return df_sma

    def calculate_rsi(
        self,
        price_series_df: DataFrame,
        window_size: int = 14
    ) -> DataFrame:
        """
        Calcule le RSI sur crypto_prices_series.
        Args:
            price_series_df: DataFrame avec colonnes coin_id, time_bucket, price_usd
            window_size: nombre de buckets pour le calcul du RSI (ex: 14)
        Return:
            DataFrame avec colonne rsi_{window_size}
        """
        w = Window.partitionBy("coin_id").orderBy("time_bucket")

        df = (
            price_series_df
            .withColumn("prev_price", F.lag("price_usd", 1).over(w))
            .withColumn("price_change", F.col("price_usd") - F.col("prev_price"))
            .withColumn("gain", F.when(F.col("price_change") > 0, F.col("price_change")).otherwise(0))
            .withColumn("loss", F.when(F.col("price_change") < 0, -F.col("price_change")).otherwise(0))
            .withColumn("avg_gain", F.avg("gain").over(w.rowsBetween(-window_size + 1, 0)))
            .withColumn("avg_loss", F.avg("loss").over(w.rowsBetween(-window_size + 1, 0)))
            .withColumn(
                "rs",
                F.when(F.col("avg_loss") == 0, F.lit(100))
                 .otherwise(F.col("avg_gain") / F.col("avg_loss"))
            )
            .withColumn(
                "rsi",
                F.lit(100) - (F.lit(100) / (F.lit(1) + F.col("rs")))
            )
            .drop("prev_price", "price_change", "gain", "loss", "avg_gain", "avg_loss", "rs")
        )
        return df

    def calculate_correlation(
        self,
        price_series_df: DataFrame,
        granularity: str = "daily"
    ) -> DataFrame:
        """
        Calcule la corrélation entre paires de cryptos sur crypto_prices_series.
        Args:
            price_series_df: DataFrame avec colonnes coin_id, time_bucket, price_usd
            granularity: granularité des données ("daily" ou "hourly")
        Return:
            DataFrame avec colonnes coin_id_1, coin_id_2, correlation, time
        """
        if granularity == "daily":
            bucket_expr = F.date_trunc("day", F.col("time_bucket"))
        else:
            bucket_expr = F.col("time_bucket")

        df_daily = price_series_df.withColumn("bucket", bucket_expr)

        df_self_join = (
            df_daily.alias("a")
            .join(
                df_daily.alias("b"),
                (F.col("a.bucket") == F.col("b.bucket")) &
                (F.col("a.coin_id") < F.col("b.coin_id")),
                "inner"
            )
            .select(
                F.col("a.coin_id").alias("coin_id_1"),
                F.col("b.coin_id").alias("coin_id_2"),
                F.col("a.bucket").alias("time_bucket"),
                F.col("a.price_usd").alias("price_1"),
                F.col("b.price_usd").alias("price_2")
            )
        )

        df_corr = (
            df_self_join
            .groupBy("coin_id_1", "coin_id_2", "time_bucket")
            .agg(F.corr("price_1", "price_2").alias("correlation"))
        )
        return df_corr

    def transform(
        self,
        input_dataframe: DataFrame
    ) -> DataFrame:
        """
        Pipeline complet : price_series + volatilité + SMA + RSI.
        """

        # Étape 1 : ajouter les indicateurs
        dataframe_with_sma = self.calculate_sma(
            input_dataframe,
            window_size=20
        )
        dataframe_with_rsi = self.calculate_rsi(
            dataframe_with_sma,
            window_size=14
        )
        dataframe_with_vol = self.calculate_volatility(
            dataframe_with_rsi,
            granularity="daily"
        )

        return dataframe_with_vol
