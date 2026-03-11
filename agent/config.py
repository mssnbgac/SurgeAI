import os
from dotenv import load_dotenv

load_dotenv()

# Blockchain Configuration
RPC_URL = os.getenv("RPC_URL", "http://localhost:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))

# Production Mode
PRODUCTION_MODE = os.getenv("PRODUCTION_MODE", "false").lower() == "true"

# Contract Addresses (update after deployment)
IDENTITY_REGISTRY = os.getenv("IDENTITY_REGISTRY_ADDRESS", "")
REPUTATION_REGISTRY = os.getenv("REPUTATION_REGISTRY_ADDRESS", "")
VALIDATION_REGISTRY = os.getenv("VALIDATION_REGISTRY_ADDRESS", "")
TRADING_AGENT = os.getenv("TRADING_AGENT_ADDRESS", "")

# Agent Configuration
AGENT_ID = int(os.getenv("AGENT_ID", "1"))
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "1000"))
MIN_PROFIT_THRESHOLD = float(os.getenv("MIN_PROFIT_THRESHOLD", "0.5"))
SLIPPAGE_TOLERANCE = float(os.getenv("SLIPPAGE_TOLERANCE", "0.01"))

# Trading Parameters
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))  # seconds
MAX_GAS_PRICE = int(os.getenv("MAX_GAS_PRICE", "50"))  # gwei
STRATEGIES = os.getenv("STRATEGIES", "arbitrage,yield,risk_management").split(",")

# DEX Routers
UNISWAP_V2_ROUTER = os.getenv("UNISWAP_V2_ROUTER", "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24")
UNISWAP_V3_ROUTER = os.getenv("UNISWAP_V3_ROUTER", "0x94cC0AaC535CCDB3C01d6787D6413C739ae12bc4")

# Token Addresses
WETH = os.getenv("WETH", "0x4200000000000000000000000000000000000006")
USDC = os.getenv("USDC", "0x036CbD53842c5426634e7929541eC2318f3dCF7e")

# Risk Management
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "5.0"))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "10.0"))
MAX_PORTFOLIO_RISK = float(os.getenv("MAX_PORTFOLIO_RISK", "25.0"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "trading_agent.log")

# Validation
if not PRIVATE_KEY and PRODUCTION_MODE:
    raise ValueError("PRIVATE_KEY must be set in production mode")

if PRODUCTION_MODE and not all([IDENTITY_REGISTRY, REPUTATION_REGISTRY, VALIDATION_REGISTRY]):
    print("⚠️  Warning: Contract addresses not set. Some features may not work.")
