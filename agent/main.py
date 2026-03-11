import asyncio
import json
from typing import Dict, List
from web3 import Web3
from eth_account import Account
import config
from strategies.arbitrage import ArbitrageStrategy
from strategies.yield_optimizer import YieldOptimizer
from strategies.risk_manager import RiskManager
from performance_tracker import PerformanceTracker
from dex_interface import UniswapV2Interface

class TradingAgent:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
        self.account = Account.from_key(config.PRIVATE_KEY) if config.PRIVATE_KEY else None
        
        # Initialize strategies
        strategy_config = {
            "MIN_PROFIT_THRESHOLD": config.MIN_PROFIT_THRESHOLD,
            "MAX_POSITION_SIZE": config.MAX_POSITION_SIZE,
            "SLIPPAGE_TOLERANCE": config.SLIPPAGE_TOLERANCE
        }
        
        self.arbitrage = ArbitrageStrategy(self.w3, strategy_config)
        self.yield_optimizer = YieldOptimizer(self.w3, strategy_config)
        self.risk_manager = RiskManager(strategy_config)
        self.performance = PerformanceTracker()
        
        # DEX interfaces
        self.uniswap_v2 = UniswapV2Interface(self.w3, config.UNISWAP_V2_ROUTER)
        
        self.positions = []
        self.running = False
        
        print(f"Trading Agent initialized")
        print(f"Agent ID: {config.AGENT_ID}")
        if self.account:
            print(f"Wallet: {self.account.address}")
        print(f"Network: {config.RPC_URL}")
    
    async def start(self):
        """Start the trading agent"""
        self.running = True
        print("\n🚀 Trading Agent started!")
        
        try:
            while self.running:
                await self.run_cycle()
                await asyncio.sleep(config.CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping agent...")
            self.running = False
    
    async def run_cycle(self):
        """Execute one trading cycle"""
        print("\n" + "="*50)
        print("Running trading cycle...")
        
        # 1. Check arbitrage opportunities
        token_pairs = [(config.WETH, config.USDC)]
        arb_opportunities = await self.arbitrage.find_opportunities(token_pairs)
        
        if arb_opportunities:
            print(f"\n💰 Found {len(arb_opportunities)} arbitrage opportunities")
            for opp in arb_opportunities:
                print(f"  - {opp['profit_pct']:.2f}% profit potential")
                await self.execute_arbitrage(opp)
        
        # 2. Check yield optimization
        if self.positions:
            rebalance_actions = await self.yield_optimizer.rebalance(self.positions)
            if rebalance_actions:
                print(f"\n📊 Found {len(rebalance_actions)} rebalancing opportunities")
                for action in rebalance_actions:
                    print(f"  - Move to {action['to_protocol']} for +{action['apy_improvement']:.2f}% APY")
        
        # 3. Risk management check
        for position in self.positions:
            risk_check = self.risk_manager.should_exit_position(
                position,
                position.get("current_price", position["entry_price"])
            )
            
            if risk_check["should_exit"]:
                print(f"\n⚠️  Risk trigger: {risk_check['reason']} ({risk_check['pnl_pct']:.2f}%)")
                await self.close_position(position)
        
        # 4. Portfolio metrics
        portfolio_risk = self.risk_manager.calculate_portfolio_risk(self.positions)
        print(f"\n📈 Portfolio: {len(self.positions)} positions, Risk Score: {portfolio_risk['risk_score']:.1f}")
    
    async def execute_arbitrage(self, opportunity: Dict):
        """Execute an arbitrage trade"""
        print(f"\n🔄 Executing arbitrage trade...")
        
        # Calculate optimal amount
        amount = self.arbitrage.calculate_optimal_amount(opportunity)
        
        # Check risk limits
        position = {
            "amount": amount,
            "entry_price": opportunity["buy_price"],
            "strategy": "arbitrage"
        }
        
        if not self.risk_manager.check_position_limits(position):
            print("❌ Position exceeds risk limits")
            return
        
        # Record trade
        trade = {
            "strategy": "arbitrage",
            "token_pair": f"{opportunity['token_a']}/{opportunity['token_b']}",
            "amount": amount,
            "entry_price": opportunity["buy_price"],
            "exit_price": opportunity["sell_price"],
            "pnl": amount * (opportunity["sell_price"] - opportunity["buy_price"]),
            "profit_pct": opportunity["profit_pct"]
        }
        
        self.performance.record_trade(trade)
        print(f"✅ Trade executed: {amount:.2f} tokens, {opportunity['profit_pct']:.2f}% profit")
        print(f"   P&L: ${trade['pnl']:.2f}")
        
        # In production: execute actual on-chain trade
        # tx = self.uniswap_v2.build_swap_tx(...)
        # signed_tx = self.account.sign_transaction(tx)
        # tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    
    async def close_position(self, position: Dict):
        """Close a trading position"""
        print(f"🔒 Closing position...")
        self.positions.remove(position)
        # In production: execute actual on-chain close

def main():
    print("""
    ╔═══════════════════════════════════════════╗
    ║   AI Trading Agent - ERC-8004 Hackathon  ║
    ║   Multi-Strategy Autonomous Trading       ║
    ╚═══════════════════════════════════════════╝
    """)
    
    agent = TradingAgent()
    
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        print("\n⏹️  Agent stopped by user")
    finally:
        # Show final performance summary
        agent.performance.print_summary()

if __name__ == "__main__":
    main()
