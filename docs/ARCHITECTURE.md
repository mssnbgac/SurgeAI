# Architecture Overview

## System Components

### 1. Smart Contracts (Solidity)

#### ERC-8004 Registries
- **IdentityRegistry**: Agent registration and identity management
- **ReputationRegistry**: Feedback and reputation tracking
- **ValidationRegistry**: Validation requests and responses

#### Trading Contract
- **TradingAgent**: Executes trades, manages positions, tracks performance

### 2. AI Agent (Python)

#### Core Strategies
- **ArbitrageStrategy**: Detects price differences across DEXs
- **YieldOptimizer**: Finds best yield opportunities
- **RiskManager**: Portfolio risk management and position sizing

#### Agent Loop
1. Scan for opportunities
2. Evaluate with risk manager
3. Execute trades on-chain
4. Update reputation registry
5. Request validation for high-value trades

### 3. Frontend Dashboard (Next.js)

- Real-time agent status
- Trade history and analytics
- Reputation score display
- Performance metrics

## Data Flow

```
User → Frontend → Smart Contracts
                      ↓
AI Agent ← Blockchain Events
    ↓
Strategy Execution
    ↓
On-chain Trade → Reputation Update
```

## Trust Layer (ERC-8004)

1. **Identity**: Agent registered with unique ID
2. **Reputation**: Clients provide feedback after trades
3. **Validation**: Third-party validators verify trade execution

## Deployment Strategy

1. Deploy registries to Base Sepolia
2. Register agent and get Agent ID
3. Deploy TradingAgent contract
4. Start Python agent with monitoring
5. Launch dashboard for visualization
