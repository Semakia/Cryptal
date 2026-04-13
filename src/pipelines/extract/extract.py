import os
from src.pipelines.extract.utils.extract_producer import CryptoDataProducer
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
COINS = os.getenv("COINS",
                  "bitcoin,ethereum,tether,binancecoin,ripple"
                  ).split(",")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
KAFKA_TOPIC_MARKET = os.getenv("KAFKA_TOPIC_MARKET", "market_data")
api_config = {
    "api_url": os.getenv("COINGECKO_BASE") + "/simple/price",
    "vs_currencies": os.getenv("VS"),
    "api_name": os.getenv("API_NAME")
}

if __name__ == "__main__":
    # Initialize the CryptoDataProducer
    producer = CryptoDataProducer(
        kafka_broker=os.getenv("KAFKA_BROKERS", "kafka:9092"),
        topic=os.getenv("KAFKA_TOPIC_MARKET", "market_data"),
        api_config=api_config,
        symbols=COINS
    )

    # Fetch and send crypto prices to Kafka topic
    producer.extract(60)
