# 🎨 Crypto Viz Dashboard - Frontend

Real-time cryptocurrency analytics dashboard built with Next.js, TypeScript, and shadcn/ui.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or pnpm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
pnpm install
# or
npm install

# Start development server
pnpm dev
# or
npm run dev
```

The app will be available at **http://localhost:3000**

---

## 📋 Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🏗️ Project Structure

```
crypto-dashboard/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Dashboard (home)
│   ├── analytics/         # Analytics view
│   ├── correlation/       # Correlation heatmap
│   └── simulator/         # P&L simulator
├── components/
│   ├── dashboard/         # Dashboard components
│   ├── analytics/         # Analytics charts
│   ├── correlation/       # Correlation heatmap
│   ├── simulator/         # Simulator components
│   ├── layout/            # Layout components
│   ├── shared/            # Shared components
│   └── ui/                # shadcn/ui components
├── hooks/
│   ├── use-crypto-data.ts # Data fetching hooks
│   └── use-toast.ts       # Toast notifications
├── lib/
│   ├── api.ts             # API client
│   ├── store.tsx          # Global state
│   └── utils.ts           # Utility functions
└── styles/
    └── globals.css        # Global styles
```

---

## 🎯 Features

### 📊 Dashboard
- Real-time cryptocurrency prices
- 24h price change indicators
- Market cap display
- Sparkline mini-charts
- Auto-refresh every 60 seconds

### 📈 Analytics
- **Volatility Analysis**: Standard deviation, CV, VaR 95%
- **Risk-Adjusted Returns**: Sharpe & Sortino ratios
- **Drawdown Analysis**: Max drawdown, underwater periods
- Interactive charts with Recharts

### 🔥 Correlation Heatmap
- Matrix visualization of crypto correlations
- Diversification score
- Best/worst correlation pairs
- Interactive tooltips

### 💼 P&L Simulator
- Investment simulation with historical data
- Compare performance across all cryptos
- Find optimal entry points
- ROI calculations

---

## 🔌 API Integration

The frontend connects to the FastAPI backend with the following endpoints:

### Data Endpoints
- `GET /api/data/prices/latest` - Latest prices
- `GET /api/data/prices/{crypto}?days=7` - Historical prices
- `GET /api/data/cryptos` - List tracked cryptos

### Metrics Endpoints
- `GET /api/metrics/volatility?period=7`
- `GET /api/metrics/sharpe?period=30`
- `GET /api/metrics/drawdown?period=30`
- `GET /api/metrics/correlation?period=30`

### Simulation Endpoints
- `POST /api/simulate/pnl` - Simulate investment
- `GET /api/simulate/pnl/compare` - Compare all cryptos
- `GET /api/simulate/best-entry/{crypto}` - Best entry point

---

## 🎨 Tech Stack

- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui
- **Charts**: Recharts
- **Data Fetching**: TanStack Query (React Query)
- **State Management**: React Context API
- **Icons**: Lucide React

---

## 📦 Key Dependencies

```json
{
  "@tanstack/react-query": "latest",
  "recharts": "latest",
  "next": "16.0.3",
  "react": "19.2.0",
  "lucide-react": "^0.454.0",
  "date-fns": "4.1.0",
  "zod": "3.25.76"
}
```

---

## 🔧 Configuration

### Period Selector

Global state manages the time period for all metrics:
- 24h (1 day)
- 7d (1 week)
- 30d (1 month)
- 90d (3 months)

### Auto-Refresh

- **Prices**: Every 60 seconds
- **Metrics**: 5 minute cache (stale time)
- **Simulations**: On-demand only

---

## 🎨 Customization

### Theme

The app supports dark/light mode via `next-themes`. Toggle in the header.

### Colors

Crypto colors are defined in `lib/utils.ts`:

```typescript
export const CRYPTO_COLORS = {
  bitcoin: "#f7931a",
  ethereum: "#627eea",
  binancecoin: "#f3ba2f",
  solana: "#14f195",
  hyperliquid: "#00d4ff",
}
```

### Add New Crypto

1. Add to backend API
2. Add color to `CRYPTO_COLORS`
3. Add name to `CRYPTO_NAMES`
4. Restart both apps

---

## 🐛 Troubleshooting

### API Connection Failed

```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify .env.local
cat .env.local

# Restart dev server
pnpm dev
```

### Port 3000 Already in Use

```bash
# Kill process
lsof -ti:3000 | xargs kill -9

# Or use different port
pnpm dev -- -p 3001
```

### Build Errors

```bash
# Clear cache and reinstall
rm -rf .next node_modules pnpm-lock.yaml
pnpm install
pnpm dev
```

---

## 📊 Performance

### Optimization Tips

1. **Lazy Loading**: Charts are lazy-loaded
2. **Caching**: React Query caches API responses
3. **Memoization**: Expensive calculations are memoized
4. **Debouncing**: User inputs are debounced

### Production Build

```bash
# Build for production
pnpm build

# Start production server
pnpm start
```

---

## 🧪 Development

### Add New Component

```bash
# Add shadcn/ui component
pnpm dlx shadcn@latest add button

# Create custom component
touch components/shared/my-component.tsx
```

### Code Style

The project uses:
- ESLint for linting
- Prettier (via ESLint config)
- TypeScript strict mode

---

## 📱 Responsive Design

The dashboard is fully responsive:
- **Mobile**: Single column layout, hamburger menu
- **Tablet**: 2 column grid
- **Desktop**: 3-4 column grid, sidebar navigation

---

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build image
docker build -t crypto-dashboard .

# Run container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 crypto-dashboard
```

---

## 📄 License

Part of the T-DAT-901 Epitech project.

---

## 👥 Support

- **API Docs**: http://localhost:8000/docs
- **Backend README**: `../src/api/README.md`
- **Project Docs**: `../docs/`

---

**Built with ❤️ for T-DAT-901 Epitech**