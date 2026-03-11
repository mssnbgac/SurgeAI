# API Documentation

## Backend API Endpoints

Base URL: `http://localhost:3001/api`

### Agent Status

**GET** `/agent/status`

Get current agent status and configuration.

Response:
```json
{
  "agentId": "1",
  "status": "active",
  "wallet": "0x...",
  "network": {
    "chainId": 84532,
    "name": "base-sepolia"
  }
}
```

### Trade History

**GET** `/agent/trades`

Get all executed trades.

Response:
```json
{
  "trades": [
    {
      "id": 1,
      "strategy": "arbitrage",
      "tokenIn": "0x...",
      "tokenOut": "0x...",
      "amountIn": "1000",
      "amountOut": "1050",
      "profit": "50",
      "timestamp": 1234567890
    }
  ],
  "totalTrades": 10,
  "totalProfit": "500"
}
```

### Reputation

