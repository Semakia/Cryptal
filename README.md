# CrypTal - Real-Time Cryptocurrency Analytics Platform

> Full-stack real-time cryptocurrency data visualization and analytics platform.

![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Kafka](https://img.shields.io/badge/Kafka-3.x-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1)
![Spark](https://img.shields.io/badge/Spark-3.5-orange)

## 📌 Overview

**t-data-901-crypto_viz** is a full-stack platform that ingests, processes, and visualizes real-time cryptocurrency price data. The architecture combines:

- **CoinGecko API** → market data source
- **Kafka** → stream ingestion and messaging
- **FastAPI** → REST API backend
- **Neon PostgreSQL** → serverless cloud database
- **Next.js** → interactive React dashboard
- **Apache Spark** → distributed analytics (SMA, RSI, volatility, correlation)


## Architecture

## 📌 Overview

**t-data-901-crypto_viz** is a full-stack platform that ingests, processes, and visualizes real-time cryptocurrency price data. The architecture combines:

- **CoinGecko API** → market data source
- **Kafka** → stream ingestion and messaging
- **FastAPI** → REST API backend
- **Neon PostgreSQL** → serverless cloud database
- **Next.js** → interactive React dashboard
- **Apache Spark** → distributed analytics (SMA, RSI, volatility, correlation)



## 📦 Data Flow

### Ingestion Flow (Real-time)

CoinGecko API
↓ (polling every X seconds)
Kafka Producer
↓
Kafka Broker → topic: crypto_prices_raw
↓
Kafka Consumer
↓
PostgreSQL (table: crypto_prices)

### Setup
### Transformation Flow (Batch/Hourly)

PostgreSQL (crypto_prices)
↓ (Spark job, periodic)
Spark Transform
├─→ crypto_price_series (Silver)
├─→ crypto_price_series_indicators (Gold)
└─→ crypto_correlation_matrix (Gold)



### Visualization Flow
Next.js Frontend
↓ (HTTP requests)
FastAPI Backend
↓ (SQL queries)
PostgreSQL


---

## 🛠️ Technology Stack

### Frontend
| Technology | Version | Usage |
|------------|---------|-------|
| Next.js | 14 | Full-stack React framework |
| React | 18 | UI components |
| Recharts / Chart.js | latest | Price & indicator charts |
| TailwindCSS | 3 | Styling |

### Backend
| Technology | Version | Usage |
|------------|---------|-------|
| FastAPI | 0.109+ | Async REST API |
| Pydantic | 2 | Data validation |
| Uvicorn | 0.27 | ASGI server |
| httpx / requests | latest | CoinGecko API calls |
| aiokafka / kafka-python | latest | Kafka consumer |

### Data Engineering
| Technology | Version | Usage |
|------------|---------|-------|
| Apache Kafka | 3.x | Message broker / streaming |
| Apache Spark | 3.5 | Distributed PySpark processing |
| Apache Airflow | 2.8 | Pipeline orchestration |
| PostgreSQL (Neon) | 15 | Serverless cloud database |

---

## Useful Commands

### View logs

```bash
cd .config/iac/dev
docker-compose logs -f
```

### Check services status

```bash
cd .config/iac/dev
docker-compose ps
```

### Restart services

```bash
cd .config/iac/dev
docker-compose restart
```

### Clean restart

```bash
cd .config/iac/dev
docker-compose down -v
cd ../../..
./start_docker.sh
```

---

## Project Structure

```
t-dat-901-crypto-viz/
├── src/
│   ├── api/                    # FastAPI backend
│   ├── pipelines/
│   │   ├── extract/           # Kafka producer
│   │   ├── load/              # Kafka consumer
│   │   └── transform/         # Analytics modules
│   └── .env                   # Environment config
├── crypto-dashboard/          # Next.js frontend
├── .config/iac/dev/           # Docker compose files
├── start_docker.sh            # Main launch script
└── README.md
```

---


---

## 🚀 Installation

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Docker and Docker Compose
- Neon account (free) → [neon.tech](https://neon.tech)

### 1. Clone the repository

```bash
git clone https://github.com/Semakia/t-data-901-crypto_viz.git
cd t-data-901-crypto_viz
```

### 2. Configure Neon Database

1. Create a project on [neon.tech](https://neon.tech)
2. Get the connection string
3. Add to `.env`:

```bash
# PostgreSQL Neon
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=crypto_prices_raw

# CoinGecko
COINGECKO_API_URL=https://api.coingecko.com/api/v3
```

### 3. Start Kafka (Docker)

```bash
cd infrastructure
docker-compose up -d kafka zookeeper
```

### 4. Start FastAPI Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start Next.js Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### 6. Run Spark Transform (optional)

```bash
docker exec spark-master spark-submit \
  --packages org.postgresql:postgresql:42.7.3,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  /opt/spark/work-dir/pipelines/transform/transform.py
```

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/prices` | Latest prices per crypto |
| `GET` | `/api/prices/{coin_id}` | Price history for a crypto |
| `GET` | `/api/indicators` | SMA, RSI, volatility |
| `GET` | `/api/indicators/{coin_id}` | Indicators for a crypto |
| `GET` | `/api/correlation` | Correlation matrix |
| `GET` | `/api/health` | Health check |

**Example:**

```bash
curl http://localhost:8000/api/prices/bitcoin
```

```json
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
```

---

## 🔧 Analytical Calculations

| Indicator | Period | Description |
|-----------|--------|-------------|
| **SMA** | 20 periods | Simple Moving Average |
| **RSI** | 14 periods | Relative Strength Index (0-100) |
| **Volatility** | 24h | Rolling standard deviation of prices |
| **Correlation** | Daily | Pearson correlation between crypto pairs |

---

## 📈 Roadmap

### Phase 1 — MVP ✅
- [x] CoinGecko ingestion → Kafka
- [x] PostgreSQL Neon storage
- [x] Spark calculations (SMA, RSI, volatility, correlation)
- [x] FastAPI REST API
- [x] Next.js frontend

### Phase 2 — In Progress
- [ ] Airflow orchestration
- [ ] Volatility threshold alerts
- [ ] E2E tests (Playwright + pytest)

### Phase 3 — Coming Soon
- [ ] Grafana dashboard
- [ ] Multi-source support (Binance, Kraken)
- [ ] Real-time WebSocket API
- [ ] Cloud deployment (AWS/GCP)

---

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Commit and push
4. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 👤 Author

**Semakia** — Data Engineer

[GitHub](https://github.com/Semakia)

