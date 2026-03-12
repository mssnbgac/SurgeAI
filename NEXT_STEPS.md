# Next Steps - Deploy Contracts

## Current Status ✅
- ✅ Hardhat node running on port 8545
- ✅ Dashboard running on port 3002
- ✅ npm packages installed (598 packages)
- ⚠️ Contracts need deployment

## Ignore These Warnings
- JSON schema warnings in VS Code → Harmless, just network connectivity
- "Calling an account which is not a contract" → Expected before deployment

## Deploy Contracts Now

### Terminal 2 (New Terminal - Keep Hardhat running in Terminal 1)

```bash
npx hardhat run scripts/deploy-testnet.ts --network localhost
```

This will:
1. Deploy all 4 contracts (Identity, Reputation, Validation, TradingAgent)
2. Register Agent ID 1
3. Mint the Agent NFT
4. Show you the contract addresses
5. Save deployment info to `deployments/` folder

### After Deployment

1. **Refresh Dashboard**: Go to http://localhost:3002 and refresh
2. **Check Connection**: Dashboard should now show:
   - Agent ID: 1
   - Contract addresses
   - Agent status

### Optional: Start Python Agent (Terminal 3)

```bash
cd agent
python main_production.py
```

This starts the AI trading agent with:
- ML price prediction
- MEV protection
- Flash loan integration
- Risk management
- Strategy optimization

## Troubleshooting

### If deployment fails with "hardhat not found"
```bash
npm install --save-dev hardhat
```

### If you get "insufficient funds"
The local Hardhat node provides 20 test accounts with 10,000 ETH each. This should never happen on localhost.

### If contracts deploy but dashboard still shows errors
1. Check the contract addresses printed after deployment
2. Verify they match what's in `.env`
3. Refresh the dashboard (Ctrl+F5 for hard refresh)

## What Happens Next

Once contracts are deployed:
- Dashboard will display agent information
- You can execute trades through the UI
- Python agent can start monitoring and trading
- All 6 hackathon features are active

## Terminal Layout

```
Terminal 1: Hardhat Node (keep running)
Terminal 2: Deploy contracts (run once, then close)
Terminal 3: Python Agent (optional, for automated trading)
Terminal 4: Dashboard (already running on port 3002)
```
