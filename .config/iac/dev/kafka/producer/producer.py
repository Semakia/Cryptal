import json
import os

import requests
from kafka import KafkaProducer
from datetime import datetime, time
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoDataProducer:
    def __init__(
        self,
        kafka_broker: str,
        topic: str,
        api_config: str = None,
        symbols: list = None,
    ):
        self.producer = KafkaProducer(
            bootstrap_servers=[kafka_broker],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        # define api_urls wich wil be use for extract data from different
        # crypto currencies
        self.api_config = api_config or {
            "api_url": "https://api.coindesk.com/v1/bpi/currentprice.json",
            "api_name": "coindesk",
            "currencies": "USD,EUR,GBP"
        }

        self.topic = topic
        self.symbols = symbols or ["bitcoin", "ethereum", "litecoin"]

    def fetch_crypto_prices(self):
        """Fetch crypto prices from the defined API URLs."""
        try:
            url = self.api_config['api_url']
            # Make a GET request to the API
            response = requests.get(
                url,
                params=self.api_config,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # Extract price based on currency
            for coin_id, prices in data.items():
                message = {
                    "source": self.api_config['api_name'],
                    'coin_id': coin_id,
                    'price_usd': prices.get('usd'),
                    'price_eur': prices.get('eur'),
                    'change_24h': prices.get('usd_24h_change'),
                    'market_cap': prices.get('usd_market_cap'),
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Send the message to Kafka
                self.producer.send(self.topic, value=message)
                logger.info(f"Sent data to Kafka: {message}")
            # Ensure all messages are sent
            self.producer.flush()
            return True
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return False

    def extract(self, interval: int):
        """Main method to extract and send crypto prices to Kafka."""

        logger.info("Starting data extraction from crypto APIs.")
        while True:
            success = self.fetch_crypto_prices()
            if success:
                logger.info("""Data extraction and sending to Kafka completed
                             successfully.""")
            else:
                logger.error("Data extraction and sending to Kafka failed.")

            # Wait for a specified interval before the next extraction
            logger.info(f"""Waiting for {interval}
                         seconds before next extraction.""")
            time.sleep(interval)


# Load environment variables from .env file
load_dotenv()
COINS = os.getenv("COINS", "bitcoin,ethereum,tether,binancecoin,ripple").split(",")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
KAFKA_TOPIC_MARKET = os.getenv("KAFKA_TOPIC_MARKET", "market_data")
api_config = {
    "api_url": os.getenv("COINGECKO_BASE") + "/simple/price",
    "currencies": os.getenv("VS"),
    "api_name": os.getenv("API_NAME")
}

if __name__ == "__main__":
    # Initialize the CryptoDataProducer
    producer = CryptoDataProducer(
        kafka_broker=os.getenv("KAFKA_BROKERS", "localhost:9092"),
        topic=os.getenv("KAFKA_TOPIC_MARKET", "market_data"),
        api_config=api_config,
        symbols=COINS
    )

    # Fetch and send crypto prices to Kafka topic
    producer.fetch_crypto_prices()
