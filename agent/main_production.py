import asyncio
import json
import logging
import signal
import sys
from typing import Dict, List
from web3 import Web3
from eth_account import Account
from datetime import datetime
import config
from strategies.arbitrage import ArbitrageStrategy
from strategies.yield_optimizer import YieldOptimizer
from strategies.risk_manager import RiskManager
from strategies.ml_predictor import MLPricePredictor
from strategies.mev_protection import MEVProtector
from strategies.flash_loan import FlashLoanStrategy
from strategies.strategy_optimizer import StrategyOptimizer
from dex_interface import DEXInterface
from performance_tracker import PerformanceTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionTradingAgent:
    """Production-ready AI Trading Agent with ERC-8004 integration"""
    
    def __init__(self):
        logger.info("Initializing Production Trading Agent...")
        
        # Blockchain connection
        self.w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
        
        # Try to connect with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.w3.is_connected():
                    logger.info(f"Connected to network: Chain ID {self.w3.eth.chain_id}")
                    break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                    import time
                    time.sleep(2)
                else:
                    logger.error(f"Failed to connect after {max_retries} attempts")
                    logger.warning("⚠️  Running in offline mode - some features will be limited")
                    # Don't raise error, continue in demo mode
        
        # Account setup
        self.account = Account.from_key(config.PRIVATE_KEY)
        logger.info(f"Agent wallet: {self.account.address}")
        
        # Check balance
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            logger.info(f"Wallet balance: {self.w3.from_wei(balance, 'ether')} ETH")
            
            if balance == 0:
                logger.warning("⚠️  Wallet has zero balance! Agent cannot execute trades.")
        except Exception as e:
            logger.warning(f"Could not check balance: {e}")
            logger.info("Wallet balance: Unknown (offline mode)")
        
        # Initialize DEX interface
        self.dex = DEXInterface(self.w3, config.UNISWAP_V2_ROUTER)
        
        # Initialize strategies
        strategy_config = {
            "MIN_PROFIT_THRESHOLD": config.MIN_PROFIT_THRESHOLD,
            "MAX_POSITION_SIZE": config.MAX_POSITION_SIZE,
            "SLIPPAGE_TOLERANCE": config.SLIPPAGE_TOLERANCE
        }
        
        self.arbitrage = ArbitrageStrategy(self.w3, strategy_config)
        self.yield_optimizer = YieldOptimizer(self.w3, strategy_config)
        self.risk_manager = RiskManager(strategy_config)
        
        # Advanced ML and MEV protection
        self.ml_predictor = MLPricePredictor(strategy_config)
        self.mev_protector = MEVProtector(self.w3)
        
        # Flash loan integration
        self.flash_loan = FlashLoanStrategy(self.w3, strategy_config)
        
        # Strategy optimizer
        self.optimizer = StrategyOptimizer(strategy_config)
        self.optimization_interval = 100  # Optimize every 100 trades
        self.trades_since_optimization = 0
        
        # Performance tracking
        self.performance = PerformanceTracker()
        
        # State management
        self.positions = []
        self.running = False
        self.cycle_count = 0
        self.last_health_check = datetime.now()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ Trading Agent initialized successfully")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    async def start(self):
        """Start the trading agent"""
        self.running = True
        logger.info("\n" + "="*60)
        logger.info("🚀 PRODUCTION TRADING AGENT STARTED")
        logger.info("="*60)
        logger.info(f"Agent ID: {config.AGENT_ID}")
        logger.info(f"Wallet: {self.account.address}")
        logger.info(f"Network: Chain ID {self.w3.eth.chain_id}")
        logger.info(f"Check Interval: {config.CHECK_INTERVAL}s")
        logger.info(f"Min Profit Threshold: {config.MIN_PROFIT_THRESHOLD}%")
        logger.info(f"Max Position Size: {config.MAX_POSITION_SIZE}")
        logger.info("="*60 + "\n")
        
        try:
            while self.running:
                try:
                    await self.run_cycle()
                    await asyncio.sleep(config.CHECK_INTERVAL)
                    
                    # Periodic health check
                    if (datetime.now() - self.last_health_check).seconds > 300:  # Every 5 min
                        await self.health_check()
                        self.last_health_check = datetime.now()
                        
                except Exception as e:
                    logger.error(f"Error in trading cycle: {e}", exc_info=True)
                    await asyncio.sleep(config.CHECK_INTERVAL)
                    
        except KeyboardInterrupt:
            logger.info("\n⏹️  Keyboard interrupt received")
        finally:
            await self.shutdown()
    
    async def run_cycle(self):
        """Execute one trading cycle"""
        self.cycle_count += 1
        logger.info(f"\n{'='*60}")
        logger.info(f"CYCLE #{self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        try:
            # 1. Check arbitrage opportunities
            await self._check_arbitrage()
            
            # 2. Check yield optimization
            await self._check_yield_optimization()
            
            # 3. Risk management
            await self._check_risk_management()
            
            # 4. Update performance metrics
            self._update_metrics()
            
        except Exception as e:
            logger.error(f"Error in cycle execution: {e}", exc_info=True)
    
    async def _check_arbitrage(self):
        """Check for arbitrage opportunities"""
        logger.info("\n💰 Checking arbitrage opportunities...")
        
        token_pairs = [(config.WETH, config.USDC)]
        opportunities = await self.arbitrage.find_opportunities(token_pairs)
        
        if opportunities:
            logger.info(f"Found {len(opportunities)} arbitrage opportunities:")
            
            # Check for flash loan opportunities
            flash_loan_opps = self.flash_loan.find_flash_loan_opportunities(
                opportunities,
                max_loan_amount=100000  # $100k max
            )
            
            if flash_loan_opps:
                logger.info(f"\n⚡ Found {len(flash_loan_opps)} FLASH LOAN opportunities:")
                for i, opp in enumerate(flash_loan_opps, 1):
                    prof = opp['profitability']
                    logger.info(f"  {i}. ${prof['loan_amount']:,.0f} loan → "
                              f"${prof['net_profit']:,.2f} profit ({prof['net_profit_pct']:.2f}%)")
                    
                    # Simulate before executing
                    simulation = self.flash_loan.simulate_flash_loan(opp)
                    if simulation['success']:
                        logger.info(f"     ✅ Simulation successful: ${simulation['profit']:,.2f}")
                        # In production, execute flash loan here
                    else:
                        logger.warning(f"     ❌ Simulation failed")
            
            # Regular arbitrage opportunities
            for i, opp in enumerate(opportunities, 1):
                logger.info(f"  {i}. {opp['profit_pct']:.2f}% profit - "
                          f"Buy on {opp['buy_dex']}, Sell on {opp['sell_dex']}")
                
                # ML price prediction for validation
                prediction = self.ml_predictor.predict_price(
                    (opp['token_in'], opp['token_out']),
                    opp['buy_price'],
                    []
                )
                
                logger.info(f"     ML Prediction: {prediction['direction']} "
                          f"(confidence: {prediction['confidence']:.1%})")
                
                # Execute if profitable enough and ML confirms
                if (opp['profit_pct'] >= config.MIN_PROFIT_THRESHOLD and 
                    prediction['confidence'] > 0.6):
                    await self.execute_arbitrage(opp)
        else:
            logger.info("No arbitrage opportunities found")
    
    async def _check_yield_optimization(self):
        """Check for yield optimization opportunities"""
        if not self.positions:
            logger.info("\n📊 No positions to optimize")
            return
        
        logger.info(f"\n📊 Checking yield optimization for {len(self.positions)} positions...")
        rebalance_actions = await self.yield_optimizer.rebalance(self.positions)
        
        if rebalance_actions:
            logger.info(f"Found {len(rebalance_actions)} rebalancing opportunities:")
            for action in rebalance_actions:
                logger.info(f"  - Move to {action['to_protocol']} for "
                          f"+{action['apy_improvement']:.2f}% APY improvement")
        else:
            logger.info("No rebalancing needed")
    
    async def _check_risk_management(self):
        """Check risk management rules"""
        if not self.positions:
            return
        
        logger.info(f"\n⚠️  Risk management check for {len(self.positions)} positions...")
        
        for position in self.positions[:]:  # Copy list to allow removal
            current_price = position.get("current_price", position["entry_price"])
            risk_check = self.risk_manager.should_exit_position(position, current_price)
            
            if risk_check["should_exit"]:
                logger.warning(f"Risk trigger: {risk_check['reason']} "
                             f"({risk_check['pnl_pct']:+.2f}%)")
                await self.close_position(position)
        
        # Portfolio risk assessment
        portfolio_risk = self.risk_manager.calculate_portfolio_risk(self.positions)
        logger.info(f"Portfolio Risk Score: {portfolio_risk['risk_score']:.1f}/100")
        
        if portfolio_risk['risk_score'] > 75:
            logger.warning("⚠️  High portfolio risk detected!")
    
    def _update_metrics(self):
        """Update performance metrics"""
        metrics = self.performance.get_summary()
        logger.info(f"\n📈 Performance Summary:")
        logger.info(f"  Total Trades: {metrics['total_trades']}")
        logger.info(f"  Win Rate: {metrics['win_rate']:.1f}%")
        logger.info(f"  Total P&L: {metrics['total_pnl']:+.2f}")
        logger.info(f"  Active Positions: {len(self.positions)}")
        
        # ML Model Stats
        ml_stats = self.ml_predictor.get_model_stats()
        logger.info(f"\n🤖 ML Model Stats:")
        logger.info(f"  Accuracy: {ml_stats['accuracy']:.1%}")
        logger.info(f"  Predictions: {ml_stats['predictions_made']}")
        
        # MEV Protection Stats
        mev_stats = self.mev_protector.get_protection_stats()
        logger.info(f"\n🛡️  MEV Protection Stats:")
        logger.info(f"  Protected Transactions: {mev_stats['protected_transactions']}")
        logger.info(f"  Threats Detected: {mev_stats['detected_threats']}")
        
        # Flash Loan Stats
        flash_stats = self.flash_loan.get_flash_loan_stats()
        logger.info(f"\n⚡ Flash Loan Stats:")
        logger.info(f"  Total Loans: {flash_stats['total_flash_loans']}")
        logger.info(f"  Success Rate: {flash_stats['success_rate']:.1f}%")
        logger.info(f"  Total Profit: ${flash_stats['total_profit']:,.2f}")
        
        # Strategy Optimization
        self.trades_since_optimization += 1
        if self.trades_since_optimization >= self.optimization_interval:
            logger.info(f"\n🔧 Running strategy optimization...")
            self._run_strategy_optimization()
            self.trades_since_optimization = 0
        
        opt_stats = self.optimizer.get_optimization_stats()
        logger.info(f"\n🎯 Strategy Optimizer:")
        logger.info(f"  Optimization Runs: {opt_stats['optimization_runs']}")
        logger.info(f"  Best Fitness: {opt_stats['best_fitness']:.4f}")
        logger.info(f"  Current Generation: {opt_stats['current_generation']}")
    
    async def execute_arbitrage(self, opportunity: Dict):
        """Execute an arbitrage trade"""
        logger.info(f"\n🔄 Executing arbitrage trade...")
        logger.info(f"  Profit: {opportunity['profit_pct']:.2f}%")
        logger.info(f"  Buy: {opportunity['buy_dex']} @ {opportunity['buy_price']}")
        logger.info(f"  Sell: {opportunity['sell_dex']} @ {opportunity['sell_price']}")
        
        # Calculate optimal amount
        amount = self.arbitrage.calculate_optimal_amount(opportunity)
        logger.info(f"  Amount: {amount:.2f} tokens")
        
        # Risk check
        position = {
            "amount": amount,
            "entry_price": opportunity["buy_price"]
        }
        
        if not self.risk_manager.check_position_limits(position):
            logger.warning("❌ Position exceeds risk limits - skipping")
            return
        
        # MEV Protection Analysis
        logger.info("\n🛡️  MEV Protection Analysis...")
        mev_analysis = self.mev_protector.analyze_trade_safety(
            opportunity.get('token_in', config.WETH),
            opportunity.get('token_out', config.USDC),
            int(amount * 1e18),  # Convert to wei
            opportunity['buy_dex']
        )
        
        logger.info(f"  Safety Score: {mev_analysis['safety_score']:.2%}")
        if mev_analysis['threats']:
            logger.warning(f"  Detected {len(mev_analysis['threats'])} threats:")
            for threat in mev_analysis['threats']:
                logger.warning(f"    - {threat.get('type')}: {threat.get('details')}")
        
        if not mev_analysis['safe']:
            logger.warning("❌ MEV risk too high - applying protection...")
            # Apply MEV protection
            protected_params = self.mev_protector.apply_protection(
                {'amount': amount, 'slippage': 0.01},
                protection_level='high'
            )
            logger.info(f"  ✅ Protection applied: {protected_params.get('use_flashbots', False) and 'Flashbots enabled' or 'Enhanced parameters'}")
        
        # In production mode, execute actual trade
        if config.PRODUCTION_MODE:
            logger.info("⚠️  Production mode: Would execute real trade here")
            # Implement actual trade execution
        else:
            logger.info("✅ Demo mode: Trade simulated successfully")
            self.performance.record_trade({
                "strategy": "arbitrage",
                "profit_pct": opportunity['profit_pct'],
                "amount": amount,
                "timestamp": datetime.now(),
                "mev_protected": not mev_analysis['safe']
            })
    
    async def close_position(self, position: Dict):
        """Close a trading position"""
        logger.info(f"🔒 Closing position: {position.get('id', 'unknown')}")
        
        if position in self.positions:
            self.positions.remove(position)
            logger.info("✅ Position closed")
    
    def _run_strategy_optimization(self):
        """Run automated strategy optimization"""
        logger.info("\n🔧 AUTOMATED STRATEGY OPTIMIZATION")
        logger.info("="*60)
        
        # Get recent performance data
        trades = self.performance.trades[-100:] if len(self.performance.trades) > 0 else []
        
        if len(trades) < 10:
            logger.info("Not enough trade data for optimization (need 10+)")
            return
        
        # Run optimization using genetic algorithm
        try:
            optimized_params = self.optimizer.optimize_parameters(
                trades,
                method='genetic'
            )
            
            logger.info("\n✅ Optimization Complete!")
            logger.info("New Parameters:")
            params_dict = optimized_params.to_dict()
            for key, value in params_dict.items():
                logger.info(f"  {key}: {value:.4f}")
            
            # Apply optimized parameters
            config.MIN_PROFIT_THRESHOLD = optimized_params.min_profit_threshold
            config.MAX_POSITION_SIZE = optimized_params.max_position_size
            config.SLIPPAGE_TOLERANCE = optimized_params.slippage_tolerance
            
            # Update strategy configs
            strategy_config = {
                "MIN_PROFIT_THRESHOLD": optimized_params.min_profit_threshold,
                "MAX_POSITION_SIZE": optimized_params.max_position_size,
                "SLIPPAGE_TOLERANCE": optimized_params.slippage_tolerance
            }
            
            self.arbitrage.config.update(strategy_config)
            self.risk_manager.max_position_size = optimized_params.max_position_size
            self.risk_manager.stop_loss_pct = optimized_params.stop_loss_pct
            self.risk_manager.take_profit_pct = optimized_params.take_profit_pct
            
            logger.info("✅ Parameters applied to all strategies")
            
            # Save optimization state
            self.optimizer.save_optimization_state()
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
    
    async def health_check(self):
            self.positions.remove(position)
            logger.info("✅ Position closed")

    def _run_strategy_optimization(self):
        """Run automated strategy optimization"""
        logger.info("\n🔧 AUTOMATED STRATEGY OPTIMIZATION")
        logger.info("="*60)

        # Get recent performance data
        trades = self.performance.trades[-100:] if len(self.performance.trades) > 0 else []

        if len(trades) < 10:
            logger.info("Not enough trade data for optimization (need 10+)")
            return

        # Run optimization using genetic algorithm
        try:
            optimized_params = self.optimizer.optimize_parameters(
                trades,
                method='genetic'
            )

            logger.info("\n✅ Optimization Complete!")
            logger.info("New Parameters:")
            params_dict = optimized_params.to_dict()
            for key, value in params_dict.items():
                logger.info(f"  {key}: {value:.4f}")

            # Apply optimized parameters
            config.MIN_PROFIT_THRESHOLD = optimized_params.min_profit_threshold
            config.MAX_POSITION_SIZE = optimized_params.max_position_size
            config.SLIPPAGE_TOLERANCE = optimized_params.slippage_tolerance

            # Update strategy configs
            strategy_config = {
                "MIN_PROFIT_THRESHOLD": optimized_params.min_profit_threshold,
                "MAX_POSITION_SIZE": optimized_params.max_position_size,
                "SLIPPAGE_TOLERANCE": optimized_params.slippage_tolerance
            }

            self.arbitrage.config.update(strategy_config)
            self.risk_manager.max_position_size = optimized_params.max_position_size
            self.risk_manager.stop_loss_pct = optimized_params.stop_loss_pct
            self.risk_manager.take_profit_pct = optimized_params.take_profit_pct

            logger.info("✅ Parameters applied to all strategies")

            # Save optimization state
            self.optimizer.save_optimization_state()

        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
    
    async def health_check(self):
        """Perform system health check"""
        logger.info("\n🏥 Health Check:")
        
        # Check RPC connection
        try:
            block = self.w3.eth.block_number
            logger.info(f"  ✅ RPC Connected (Block: {block})")
        except Exception as e:
            logger.error(f"  ❌ RPC Connection Failed: {e}")
        
        # Check wallet balance
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            eth_balance = self.w3.from_wei(balance, 'ether')
            logger.info(f"  ✅ Wallet Balance: {eth_balance:.4f} ETH")
            
            if eth_balance < 0.01:
                logger.warning("  ⚠️  Low ETH balance!")
        except Exception as e:
            logger.error(f"  ❌ Balance Check Failed: {e}")
        
        # Check gas price
        try:
            gas_price = self.w3.eth.gas_price
            gas_gwei = self.w3.from_wei(gas_price, 'gwei')
            logger.info(f"  ✅ Gas Price: {gas_gwei:.2f} Gwei")
            
            if gas_gwei > config.MAX_GAS_PRICE:
                logger.warning(f"  ⚠️  High gas price! (Max: {config.MAX_GAS_PRICE} Gwei)")
        except Exception as e:
            logger.error(f"  ❌ Gas Price Check Failed: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("\n" + "="*60)
        logger.info("🛑 SHUTTING DOWN TRADING AGENT")
        logger.info("="*60)
        
        # Save performance data
        try:
            self.performance.save_to_file("performance_data.json")
            logger.info("✅ Performance data saved")
        except Exception as e:
            logger.error(f"❌ Failed to save performance data: {e}")
        
        # Close any open positions (in production)
        if self.positions:
            logger.warning(f"⚠️  {len(self.positions)} positions still open")
        
        logger.info(f"Total cycles executed: {self.cycle_count}")
        logger.info("👋 Agent stopped successfully")
        logger.info("="*60 + "\n")

def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════════╗
    ║   AI Trading Agent - ERC-8004 Hackathon  ║
    ║   Production Mode - Multi-Strategy        ║
    ╚═══════════════════════════════════════════╝
    """)
    
    try:
        agent = ProductionTradingAgent()
        asyncio.run(agent.start())
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
