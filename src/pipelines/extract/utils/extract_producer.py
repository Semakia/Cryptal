import json
import logging
import os
import time
from datetime import datetime

import requests
from kafka import KafkaProducer

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
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

        # define api_urls wich wil be use for extract data from different
        # crypto currencies
        self.api_config = api_config or {
            "api_url": "https://api.coindesk.com/v1/bpi/currentprice.json",
            "api_name": "coindesk",
            "vs_currencies": "USD,EUR,GBP",
        }

        self.topic = topic
        self.symbols = symbols or ["bitcoin", "ethereum", "litecoin"]

    def fetch_crypto_prices(self):
        """Fetch crypto prices from the defined API URLs."""
        try:
            url = self.api_config["api_url"]
            # Make a GET request to the API
            params = {
                "ids": ",".join(self.symbols),
                "vs_currencies": self.api_config["vs_currencies"],
                "include_24hr_change": "true",
                "include_market_cap": "true",
            }
            response = requests.get(url, params=params, timeout=10)

            response.raise_for_status()
            data = response.json()

            # Extract price based on currency
            for coin_id, prices in data.items():
                message = {
                    "source": self.api_config["api_name"],
                    "currency": self.api_config["vs_currencies"],
                    "coin_id": coin_id,
                    "price_usd": prices.get("usd"),
                    "price_eur": prices.get("eur"),
                    "price_gbp": prices.get("gbp"),
                    "change_24h": prices.get("usd_24h_change"),
                    "market_cap": prices.get("usd_market_cap"),
                    "timestamp": datetime.utcnow().isoformat(),
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
                logger.info(
                    "Data extraction and sending to Kafka completed successfully."
                )
            else:
                logger.error("Data extraction and sending to Kafka failed.")

            # Wait for a specified interval before the next extraction
            logger.info(f"Waiting for {interval} seconds before next extraction.")
            time.sleep(interval)
