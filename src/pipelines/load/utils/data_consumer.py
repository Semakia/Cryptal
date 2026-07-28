import json
import logging

import psycopg2
from kafka import KafkaConsumer

from src.pipelines.quality.validator import validate_record

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoDataConsumer:
    """
    Utility class for consuming crypto data from Kafka
     and loading it into a database.

    Applique un contrôle qualité à l'ingestion : les messages invalides sont
    écartés vers `crypto_prices_rejected` (dead-letter), les doublons ignorés.

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

            # Dead-letter : messages écartés par le contrôle qualité.
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS crypto_prices_rejected (
                    id SERIAL PRIMARY KEY,
                    payload JSONB,
                    reasons TEXT,
                    rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            self.conn.commit()

        # Durcissement best-effort (n'échoue jamais l'init : la donnée héritée
        # peut violer une contrainte ; la validation à l'ingestion garantit que
        # les NOUVELLES lignes sont propres).
        self._harden_schema()

        logger.info("Database initialized successfully.")

    def _harden_schema(self):
        """Ajoute contraintes CHECK et index d'unicité, sans casser l'init."""
        statements = [
            # Prix strictement positif.
            """
            DO $$ BEGIN
                ALTER TABLE crypto_prices
                    ADD CONSTRAINT chk_price_usd_positive CHECK (price_usd > 0);
            EXCEPTION WHEN others THEN NULL; END $$;
            """,
            # Capitalisation non négative.
            """
            DO $$ BEGIN
                ALTER TABLE crypto_prices
                    ADD CONSTRAINT chk_market_cap_non_negative CHECK (market_cap >= 0);
            EXCEPTION WHEN others THEN NULL; END $$;
            """,
            # Déduplication (coin_id, timestamp). Échoue si doublons hérités.
            """
            DO $$ BEGIN
                CREATE UNIQUE INDEX IF NOT EXISTS uq_crypto_prices_coin_ts
                    ON crypto_prices (coin_id, timestamp);
            EXCEPTION WHEN others THEN NULL; END $$;
            """,
        ]
        for stmt in statements:
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(stmt)
                self.conn.commit()
            except Exception as e:  # pragma: no cover - défense best-effort
                self.conn.rollback()
                logger.warning(f"Durcissement schéma ignoré: {e}")

    def _store_rejected(self, message: dict, reasons: list):
        """Enregistre un message écarté dans la table dead-letter."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO crypto_prices_rejected (payload, reasons)
                    VALUES (%s::jsonb, %s);
                    """,
                    (json.dumps(message, default=str), "; ".join(reasons)),
                )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Impossible d'enregistrer le rejet: {e}")

    def load_message_in_db(self, message: dict) -> bool:
        """
        Valide puis insère un message. Les messages invalides partent en
        dead-letter ; les doublons sont ignorés.

        Returns
        -------
        bool
            True si le message a été traité (inséré ou doublon ignoré),
            False s'il a été rejeté ou si l'insertion a échoué.
        """
        reasons = validate_record(message)
        if reasons:
            logger.warning(
                f"Rejet qualité coin_id={message.get('coin_id')!r}: {reasons}"
            )
            self._store_rejected(message, reasons)
            return False

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
                self.conn.commit()
            logger.info(f"Inserted message into DB: {message}")
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            logger.info(
                f"Doublon ignoré: {message.get('coin_id')} @ {message.get('timestamp')}"
            )
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting message into DB: {e}")
            return False
        return True

    def load_data(self):
        """Consume Kafka and insert in database."""
        for msg in self.consumer:
            logger.info(f"Received message: {msg.value}")
            self.load_message_in_db(msg.value)
