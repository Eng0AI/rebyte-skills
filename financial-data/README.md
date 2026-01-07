# Financial Data Skill

Access US stock market data via eng0's data API.

## Data Available

| Endpoint | Data |
|----------|------|
| `/stocks/bars` | OHLCV price bars (1min - 1week) |
| `/stocks/news` | News with sentiment analysis |
| `/stocks/details` | Company info, market cap |

## Coverage

- All US stock tickers
- 5 years historical data
- 15-minute delayed quotes

## Quick Examples

### Get Daily Prices
```bash
curl -X POST https://api.eng0.ai/api/data/stocks/bars \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL", "interval": "1day", "from": "2024-12-01", "to": "2024-12-31"}'
```

### Get News with Sentiment
```bash
curl -X POST https://api.eng0.ai/api/data/stocks/news \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TSLA", "limit": 10}'
```

### Get Company Details
```bash
curl -X POST https://api.eng0.ai/api/data/stocks/details \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA"}'
```

## Complements

- **financial-skill** → SEC filings (EdgarTools)
- **financial-deep-research** → Research reports
