import json
import logging
from datetime import datetime

from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoDataConsumer:
    """
    Utility class for consuming crypto data from Kafka
     and loading it into a database.

    Parameters
    ----------
    db_connection : connection
        The database connection object.
    kafka_broker : str
        The Kafka broker address.
    topic : str
        The Kafka topic to consume from.
    """

    def __init__(self, db_connection, kafka_broker: str, topic: str):
        # Connexion DB
        self.conn = db_connection

        # Consumer Kafka
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[kafka_broker],
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="crypto_data_consumers",
        )

    def init_database(self):
        """
        Initialize the database by creating necessary tables and indexes.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS crypto_prices (
                    id SERIAL PRIMARY KEY,
                    source VARCHAR(50),
                    currency VARCHAR(10),
                    coin_id VARCHAR(50),
                    price_usd FLOAT,
                    price_eur FLOAT,
                    price_gbp FLOAT,
                    change_24h FLOAT,
                    market_cap BIGINT,
                    timestamp TIMESTAMP,
                    dt_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    dt_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_crypto_prices
                    ON crypto_prices (coin_id, timestamp);
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_currency
                    ON crypto_prices (currency);
                """
            )

            cursor.connection.commit()

        logger.info("Database initialized successfully.")

    def load_message_in_db(self, message: dict) -> bool:
        """
        Inserts a message into the appropriate database table.

        Parameters
        ----------
        message : dict
            The message to be inserted into the database.

        Returns
        -------
        bool
            True if insertion was successful, False otherwise.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO crypto_prices (
                        source, currency, coin_id,
                        price_usd, price_eur, price_gbp,
                        change_24h, market_cap, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        message["source"],
                        message["currency"],
                        message["coin_id"],
                        message["price_usd"],
                        message["price_eur"],
                        message["price_gbp"],
                        message["change_24h"],
                        message["market_cap"],
                        message["timestamp"],
                    ),
                )
                cursor.connection.commit()
            logger.info(f"Inserted message into DB: {message}")
        except Exception as e:
            logger.error(f"Error inserting message into DB: {e}")
            return False
        return True

    def load_data(self):
        """Consume Kafka and insert in database."""
        for msg in self.consumer:
            logger.info(f"Received message: {msg.value}")
            self.load_message_in_db(msg.value)
