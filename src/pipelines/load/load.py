import os

import psycopg2
from dotenv import load_dotenv
from src.pipelines.load.utils.data_consumer import CryptoDataConsumer

# Load environment variables from .env file
load_dotenv()
COINS = os.getenv("COINS", "bitcoin,ethereum,tether,binancecoin,ripple").split(",")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
KAFKA_TOPIC_MARKET = os.getenv("KAFKA_TOPIC_MARKET", "market_data")
DB_HOST = os.getenv("BRONZE_DB_HOST")
DB_NAME = os.getenv("BRONZE_DB_NAME")
DB_USER = os.getenv("BRONZE_DB_USER")
DB_PORT = os.getenv("BRONZE_DB_PORT", "5432")
DB_PASSWORD = os.getenv("BRONZE_DB_PASSWORD")

db_connection_string = f"""
    host={DB_HOST} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} port={DB_PORT} sslmode=require
"""
db_conn = psycopg2.connect(db_connection_string)

if __name__ == "__main__":
    # Initialize the CryptoDataConsumer
    consumer = CryptoDataConsumer(
        db_connection=db_conn,
        kafka_broker=KAFKA_BROKERS,
        topic=KAFKA_TOPIC_MARKET,
    )

    # Fetch and send crypto prices and news to Kafka topic

    try:
        consumer.init_database()
        consumer.load_data()
    finally:
        db_conn.close()
