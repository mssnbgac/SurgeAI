import express from 'express';
import { ethers } from 'ethers';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(express.json());

const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);

// Contract addresses (set after deployment)
const IDENTITY_REGISTRY = process.env.IDENTITY_REGISTRY_ADDRESS || '';
const REPUTATION_REGISTRY = process.env.REPUTATION_REGISTRY_ADDRESS || '';
const VALIDATION_REGISTRY = process.env.VALIDATION_REGISTRY_ADDRESS || '';
const TRADING_AGENT = process.env.TRADING_AGENT_ADDRESS || '';

// API Routes
app.get('/api/agent/status', async (req, res) => {
  try {
    res.json({
      agentId: process.env.AGENT_ID,
      status: 'active',
      wallet: wallet.address,
      network: await provider.getNetwork()
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get status' });
  }
});

app.get('/api/agent/trades', async (req, res) => {
  try {
    // Fetch trade history from contract
    res.json({
      trades: [],
      totalTrades: 0,
      totalProfit: 0
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get trades' });
  }
});

app.get('/api/agent/reputation', async (req, res) => {
  try {
    // Fetch reputation from ReputationRegistry
    res.json({
      score: 95,
      feedbackCount: 12,
      validations: 8
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to get reputation' });
  }
});

app.post('/api/agent/execute-trade', async (req, res) => {
  try {
    const { strategy, tokenIn, tokenOut, amount } = req.body;
    
    // Execute trade through TradingAgent contract
    res.json({
      success: true,
      txHash: '0x...',
      strategy
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to execute trade' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`🚀 Backend server running on port ${PORT}`);
});
