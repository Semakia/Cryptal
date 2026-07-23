# CrypTal - Real-Time Cryptocurrency Analytics Platform

> Full-stack real-time cryptocurrency data visualization and analytics platform.

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Kafka](https://img.shields.io/badge/Kafka-3.x-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1)
![Spark](https://img.shields.io/badge/Spark-3.5-orange)

---


## 📌 Overview

**Cryptal** is a full-stack platform that ingests, processes, and visualizes real-time cryptocurrency price data. It follows a modern **extract → load → transform** pipeline architecture with Kafka as the messaging backbone.

### Key Components
- **CoinGecko API** → market data source
- **Kafka** → stream ingestion and messaging
- **FastAPI** → REST API backend
- **Neon PostgreSQL** → serverless cloud database
- **Next.js** → interactive React dashboard
- **Apache Spark** → distributed analytics (SMA, RSI, volatility, correlation)

---


## 🏗️ Architecture

                        ┌─────────────────────────────────────┐
                        │           COINGECKO API              │
                        │         (Data Source)                │
                        └────────────────┬────────────────────┘
                                         │ (polling)
                                         ▼
               ┌─────────────────────────────────────────────────────────────────┐
               │ EXTRACT LAYER │
               │ src/pipelines/extract/ → Kafka Producer │
               │ (CoinGecko → Kafka topic: crypto_prices_raw) │
               └───────────────────────────────┬─────────────────────────────────┘
               │
               ▼
               ┌─────────────────────────────────────────────────────────────────┐
               │ LOAD LAYER │
               │ src/pipelines/load/ → Kafka Consumer → PostgreSQL Neon │
               │ (Kafka → crypto_prices table) │
               └───────────────────────────────┬─────────────────────────────────┘
               │
               ▼
               ┌─────────────────────────────────────────────────────────────────┐
               │ TRANSFORM LAYER │
               │ src/pipelines/transform/ → Apache Spark │
               │ - crypto_prices_series (Silver) │
               │ - crypto_price_indicators (Gold) │
               │ - crypto_correlation_matrix (Gold) │
               └───────────────────────────────┬─────────────────────────────────┘
               │
               ▼
               ┌─────────────────────────────────────────────────────────────────┐
               │ PRESENTATION LAYER │
               │ src/api/ → FastAPI REST API │
               │ crypto-dashboard/ → Next.js Frontend │
               └─────────────────────────────────────────────────────────────────┘



---

## 📦 Data Flow

     CoinGecko API
     ↓ (polling every X seconds)
     [EXTRACT] Kafka Producer (PySpark)
     ↓
     Kafka Broker → topic: crypto_prices_raw
     ↓
     [LOAD] Kafka Consumer (FastAPI service)
     ↓
     PostgreSQL Neon (table: crypto_prices)
     ↓
     [TRANSFORM] Spark Job (periodic)
     ├─→ crypto_prices_series (Silver)
     ├─→ crypto_price_indicators (Gold)
     └─→ crypto_correlation_matrix (Gold)
     ↓
     [API] FastAPI → [FRONTEND] Next.js Dashboard


---

## 🛠️ Technology Stack

| Layer | Technology | Usage |
|-------|------------|-------|
| **Extract** | Python + PySpark | CoinGecko API polling → Kafka |
| **Load** | aiokafka / kafka-python | Kafka consumer → PostgreSQL |
| **Transform** | Apache Spark 3.5 | SMA, RSI, volatility, correlation |
| **API** | FastAPI 0.109+ | REST endpoints |
| **Frontend** | Next.js 14 + React 18 | Interactive dashboard |
| **Database** | PostgreSQL (Neon) | Serverless cloud storage |
| **Infra** | Docker Compose | Local development environment |

---

## 📁 Project Structure

     t-data-901-crypto_viz/
     │
     ├── .config/
     │   └── iac/
     │       └── dev/                      # Docker Compose (dev)
     │           ├── docker-compose.yml
     │           ├── kafka/
     │           ├── pgadmin/
     │           ├── postgres/
     │           └── spark/
     │
     ├── crypto-dashboard/                 # Next.js Frontend
     │   ├── app/                          # Pages: dashboard, analytics, correlation, simulator
     │   ├── components/                   # shadcn/ui, Recharts charts
     │   ├── hooks/                        # use-crypto-data, use-toast
     │   ├── lib/                          # API client, store, utils
     │   ├── public/
     │   ├── styles/
     │   ├── .env.example
     │   ├── Dockerfile
     │   ├── next.config.mjs
     │   ├── package.json (pnpm)
     │   └── README.md
     │
     ├── docs/
     │   └── t_dat_901_crypto_viz (1).pdf  # Documentation projet Epitech
     │
     ├── scripts/                          # Scripts utilitaires
     │   ├── clean_old_cryptos.py
     │   ├── diagnose_drawdown.sh
     │   ├── seed_historical_data.py
     │   ├── seed_historical_data_v2.py
     │   ├── seed_historical_data_v3.py
     │   ├── start_api.sh
     │   ├── start_full_stack.sh
     │   ├── test_api.py
     │   ├── test_correlation.py
     │   ├── test_drawdown.py
     │   ├── test_fixed_metrics.sh
     │   ├── test_neon_data.py
     │   ├── test_pnl_simulator.py
     │   ├── test_sharpe.py
     │   ├── test_volatility.py
     │   └── verify_metrics_corrections.sh
     │
     ├── src/
     │   ├── .env.example                  # Variables d'environnement
     │   │
     │   ├── api/                          # FastAPI Backend
     │   │   ├── __init__.py
     │   │   ├── __main__.py
     │   │   ├── main.py
     │   │   ├── database.py               # Connexion Neon PostgreSQL
     │   │   ├── models.py                 # Pydantic schemas
     │   │   ├── requirements.txt
     │   │   ├── Dockerfile
     │   │   └── routers/
     │   │       ├── __init__.py
     │   │       ├── data.py               # GET /api/data/*
     │   │       ├── health.py             # GET /api/health
     │   │       ├── metrics.py            # GET /api/metrics/*
     │   │       └── simulation.py         # POST /api/simulate/*
     │   │
     │   ├── pipelines/                    # ETL Kafka → Spark
     │   │   │
     │   │   ├── extract/                  # Kafka Producer (CoinGecko → Kafka)
     │   │   │   ├── extract.py
     │   │   │   └── utils/
     │   │   │       └── extract_producer.py
     │   │   │
     │   │   ├── load/                     # Kafka Consumer (Kafka → PostgreSQL)
     │   │   │   ├── load.py
     │   │   │   └── utils/
     │   │   │       └── data_consumer.py
     │   │   │
     │   │   └── transform/                # Analytics (Spark)
     │   │       ├── transform.py
     │   │       ├── correlation_calculator.py
     │   │       ├── drawdown_calculator.py
     │   │       ├── portfolio_simulator.py
     │   │       ├── sharpe_calculator.py
     │   │       ├── volatility_calculator.py
     │   │       └── utils/
     │   │           ├── data_transformer.py
     │   │           └── database_reader.py
     │   │
     │   ├── test/
     │   │   └── test.py
     │   │
     │   └── utils/
     │       └── utils.py
     │
     ├── .gitignore
     ├── .gitlab-ci.yml
     ├── README.md
     ├── start_docker.sh
     └── LICENSE

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Neon account (free) → [neon.tech](https://neon.tech)
## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Neon account (free) → [neon.tech](https://neon.tech)

### 1. Clone the repository
### 1. Clone the repository

```bash
git clone https://github.com/Semakia/t-data-901-crypto_viz.git
cd t-data-901-crypto_viz

### 2. Configure environment variables
Edit src/.env:
# PostgreSQL Neon
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=crypto_prices_raw

# CoinGecko
COINGECKO_API_URL=https://api.coingecko.com/api/v3

# Spark
SPARK_HOME=/opt/spark
git clone https://github.com/Semakia/t-data-901-crypto_viz.git
cd t-data-901-crypto_viz

### 2. Configure environment variables
Edit src/.env:
# PostgreSQL Neon
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=crypto_prices_raw

# CoinGecko
COINGECKO_API_URL=https://api.coingecko.com/api/v3

# Spark
SPARK_HOME=/opt/spark
```

### 3. Start all services
### 3. Start all services
```bash
chmod +x start_docker.sh
chmod +x start_docker.sh
./start_docker.sh
```

This script will:

Start Kafka and Zookeeper (Docker Compose)

Start PostgreSQL (local or connect to Neon)

Launch the FastAPI backend
Launch the Spark cluster (optional)

### 4. Start the frontend
cd crypto-dashboard
npm install
npm run dev
Open http://localhost:3000

## 📊 API Endpoints

| Method | Endpoint                  | Description                |
| ------ | ------------------------- | -------------------------- |
| GET    | /api/prices               | Latest prices per crypto   |
| GET    | /api/prices/{coin_id}     | Price history for a crypto |
| GET    | /api/indicators           | SMA, RSI, volatility       |
| GET    | /api/indicators/{coin_id} | Indicators for a crypto    |
| GET    | /api/correlation          | Correlation matrix         |
| GET    | /api/health               | Health check               |

Example:
curl http://localhost:8000/api/prices/bitcoin

{
  "coin_id": "bitcoin",
  "data": [
    {
      "time_bucket": "2026-04-14T22:00:00Z",
      "price_usd": 68542.30,
      "sma_20": 67234.15,
      "rsi": 58.4,
      "volatility": 1247.82
    }
  ]
}

## 🔧 Analytical Calculations
| Indicator   | Period     | Description                       |
| ----------- | ---------- | --------------------------------- |
| SMA         | 20 periods | Simple Moving Average             |
| RSI         | 14 periods | Relative Strength Index (0-100)   |
| Volatility  | 24h        | Rolling standard deviation        |
| Correlation | Daily      | Pearson correlation between pairs |

## 🤝 Contributing
Fork the project

Create a feature branch

Commit and push

Open a Pull Request

📄 License
MIT License — see LICENSE

👤 Author
Semakia — Data Engineer
This script will:

Start Kafka and Zookeeper (Docker Compose)

Start PostgreSQL (local or connect to Neon)

Launch the FastAPI backend
Launch the Spark cluster (optional)

### 4. Start the frontend
cd crypto-dashboard
npm install
npm run dev
Open http://localhost:3000

## 📊 API Endpoints

| Method | Endpoint                  | Description                |
| ------ | ------------------------- | -------------------------- |
| GET    | /api/prices               | Latest prices per crypto   |
| GET    | /api/prices/{coin_id}     | Price history for a crypto |
| GET    | /api/indicators           | SMA, RSI, volatility       |
| GET    | /api/indicators/{coin_id} | Indicators for a crypto    |
| GET    | /api/correlation          | Correlation matrix         |
| GET    | /api/health               | Health check               |

Example:
curl http://localhost:8000/api/prices/bitcoin

{
  "coin_id": "bitcoin",
  "data": [
    {
      "time_bucket": "2026-04-14T22:00:00Z",
      "price_usd": 68542.30,
      "sma_20": 67234.15,
      "rsi": 58.4,
      "volatility": 1247.82
    }
  ]
}

## 🔧 Analytical Calculations
| Indicator   | Period     | Description                       |
| ----------- | ---------- | --------------------------------- |
| SMA         | 20 periods | Simple Moving Average             |
| RSI         | 14 periods | Relative Strength Index (0-100)   |
| Volatility  | 24h        | Rolling standard deviation        |
| Correlation | Daily      | Pearson correlation between pairs |

## 🤝 Contributing
Fork the project

Create a feature branch

Commit and push

Open a Pull Request

📄 License
MIT License — see LICENSE

👤 Author
Semakia — Data Engineer
