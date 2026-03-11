# Deployment Guide

## Prerequisites

- Node.js v18+ and npm
- Python 3.9+
- MetaMask or similar wallet
- Base Sepolia testnet ETH (get from [faucet](https://www.coinbase.com/faucets/base-ethereum-goerli-faucet))

## Step 1: Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` with your configuration:
```env
# Blockchain
PRIVATE_KEY=your_private_key_here
BASE_SEPOLIA_RPC=https://sepolia.base.org

# Agent Configuration
AGENT_ID=1
MAX_POSITION_SIZE=1000
MIN_PROFIT_THRESHOLD=0.5
SLIPPAGE_TOLERANCE=0.01
```

## Step 2: Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
cd agent
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## Step 3: Compile Contracts

```bash
npx hardhat compile
```

## Step 4: Run Tests

```bash
npx hardhat test
```

## Step 5: Deploy to Base Sepolia

```bash
npm run deploy:testnet
```

This will deploy:
- IdentityRegistry
- ReputationRegistry
- ValidationRegistry
- TradingAgent

Save the deployed contract addresses to your `.env` file.

## Step 6: Register Agent

After deployment, your agent is automatically registered with ID 1. Update the registration file:

```bash
# Edit agent/registration.json with your deployed addresses
```

## Step 7: Start the Agent

```bash
cd agent
python main.py
```

## Step 8: Start the Dashboard

In a new terminal:

```bash
cd frontend
npm run dev
```

Visit http://localhost:3002 to see your dashboard.

## Testnet Addresses

### Base Sepolia
- Chain ID: 84532
- RPC: https://sepolia.base.org
- Explorer: https://sepolia.basescan.org

### Test Tokens
- WETH: 0x4200000000000000000000000000000000000006
- USDC: 0x036CbD53842c5426634e7929541eC2318f3dCF7e

## Troubleshooting

### "Insufficient funds"
Get testnet ETH from the Base Sepolia faucet.

### "Contract not deployed"
Make sure you ran `npm run deploy:testnet` and updated your `.env` file.

### "Python module not found"
Run `pip install -r agent/requirements.txt`

### "Cannot connect to RPC"
Check your RPC URL in `.env` and ensure you have internet connectivity.

## Production Deployment

For mainnet deployment:

1. Update `hardhat.config.ts` with mainnet network
2. Ensure you have sufficient ETH for gas
3. Run: `npm run deploy:mainnet`
4. Update all contract addresses in `.env`
5. Test thoroughly before enabling autonomous trading

## Security Notes

- Never commit your `.env` file
- Use a dedicated wallet for the agent
- Start with small position sizes
- Monitor the agent closely
- Set appropriate risk limits

## Prerequisites

1. Node.js v18+ and npm
2. Python 3.9+
3. Hardhat
4. MetaMask or similar wallet

## Step 1: Install Dependencies

### Smart Contracts
```bash
npm install
```

### Frontend
```bash
cd frontend
npm install
```

### Backend
```bash
cd backend
npm install
```

### AI Agent
```bash
cd agent
pip install -r requirements.txt
```

## Step 2: Configure Environment

Copy `.env.example` to `.env` and fill in:

```bash
# Blockchain
PRIVATE_KEY=your_private_key_here
RPC_URL=https://sepolia.base.org
BASE_SEPOLIA_RPC=https://sepolia.base.org

# Contract Addresses (fill after deployment)
IDENTITY_REGISTRY_ADDRESS=
REPUTATION_REGISTRY_ADDRESS=
VALIDATION_REGISTRY_ADDRESS=
TRADING_AGENT_ADDRESS=
AGENT_ID=1

# Agent Configuration
MIN_PROFIT_THRESHOLD=0.5
MAX_POSITION_SIZE=1000
SLIPPAGE_TOLERANCE=0.01
CHECK_INTERVAL=60

# Tokens (Base Sepolia)
WETH=0x4200000000000000000000000000000000000006
USDC=0x036CbD53842c5426634e7929541eC2318f3dCF7e
```

## Step 3: Deploy Smart Contracts

### Local Testing
```bash
# Start local node
npx hardhat node

# Deploy (in another terminal)
npm run deploy:local
```

### Testnet Deployment (Base Sepolia)
```bash
npm run deploy:testnet
```

Save the deployed contract addresses to your `.env` file.

## Step 4: Verify Contracts (Optional)

```bash
npx hardhat verify --network baseSepolia <CONTRACT_ADDRESS>
```

## Step 5: Start Backend Server

```bash
cd backend
npm run dev
```

Server runs on `http://localhost:3001`

## Step 6: Start Frontend

```bash
cd frontend
npm run dev
```

Dashboard available at `http://localhost:3002`

## Step 7: Run AI Agent

```bash
cd agent
python main.py
```

## Testing

Run contract tests:
```bash
npm test
```

## Troubleshooting

### "Insufficient funds" error
- Ensure your wallet has testnet ETH
- Get Base Sepolia ETH from: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet

### "Nonce too high" error
- Reset your MetaMask account in Settings > Advanced > Clear activity tab data

### Python dependencies issues
- Use a virtual environment: `python -m venv venv && source venv/bin/activate`
