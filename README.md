# CrypTal - Real-Time Cryptocurrency Analytics Platform

T-DAT-901 Epitech Project

A full-stack application for real-time cryptocurrency analysis with continuous data collection, processing, and visualization.

---

## Architecture

```
Frontend (Next.js)  →  Backend API (FastAPI)  →  PostgreSQL (Neon)
                                                        ↑
                                                   Kafka Consumer
                                                        ↑
                                                   Kafka Broker
                                                        ↑
                                                   Kafka Producer
                                                        ↑
                                                   CoinGecko API
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose

### Setup

1. Copy the environment template:

```bash
cp src/.env.example src/.env
```

2. Edit `src/.env` with your Neon database credentials:

```env
BRONZE_DB_NAME=neondb
BRONZE_DB_HOST=your-neon-host.neon.tech
BRONZE_DB_USER=your_db_user
BRONZE_DB_PASSWORD=your_db_password
```

Ask your team lead for the actual credentials.

### Launch

```bash
./start_docker.sh
```

### Access

- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop

```bash
cd .config/iac/dev
docker-compose down
```

---

## Features

- Real-time cryptocurrency price tracking (Bitcoin, Ethereum, BNB, Solana, Hyperliquid)
- Advanced analytics (volatility, Sharpe ratio, drawdown, correlation)
- Interactive charts and visualizations
- Investment P&L simulator
- Auto-refresh every 60 seconds

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

## Tech Stack

**Backend**: Python 3.11, FastAPI, Kafka, PostgreSQL/Neon  
**Frontend**: Next.js 15, TypeScript, Tailwind CSS, Recharts  
**Infrastructure**: Docker, Docker Compose

---

## Troubleshooting

### No data in dashboard

Wait 5-10 minutes after first launch for data accumulation.

### Port already in use

```bash
cd .config/iac/dev
docker-compose down
```

### Platform warning on Apple Silicon

Services will run via emulation. No action required.

---

## Documentation

- Documentation: `doc/rapport.tex`

---

## Team

T-DAT-901 Epitech Project
