from typing import Dict, List
import json
from datetime import datetime
import numpy as np

class PerformanceTracker:
    """Track and analyze trading performance"""
    
    def __init__(self, save_file: str = "performance.json"):
        self.save_file = save_file
        self.trades: List[Dict] = []
        self.load_history()
    
    def load_history(self):
        """Load trade history from file"""
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                self.trades = data.get('trades', [])
        except FileNotFoundError:
            self.trades = []
    
    def save_history(self):
        """Save trade history to file"""
        with open(self.save_file, 'w') as f:
            json.dump({'trades': self.trades}, f, indent=2)
    
    def record_trade(self, trade: Dict):
        """Record a new trade"""
        trade['timestamp'] = datetime.now().isoformat()
        self.trades.append(trade)
        self.save_history()
    
    def get_total_pnl(self) -> float:
        """Calculate total profit/loss"""
        return sum(t.get('pnl', 0) for t in self.trades)
    
    def get_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if not self.trades:
            return 0.0
        
        wins = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        return (wins / len(self.trades)) * 100
    
    def get_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(self.trades) < 2:
            return 0.0
        
        returns = [t.get('pnl', 0) for t in self.trades]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return (avg_return - risk_free_rate) / std_return
    
    def get_max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if not self.trades:
            return 0.0
        
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for trade in self.trades:
            cumulative += trade.get('pnl', 0)
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    def get_strategy_performance(self) -> Dict[str, Dict]:
        """Get performance breakdown by strategy"""
        strategies = {}
        
        for trade in self.trades:
            strategy = trade.get('strategy', 'unknown')
            if strategy not in strategies:
                strategies[strategy] = {
                    'count': 0,
                    'total_pnl': 0,
                    'wins': 0,
                    'losses': 0
                }
            
            strategies[strategy]['count'] += 1
            pnl = trade.get('pnl', 0)
            strategies[strategy]['total_pnl'] += pnl
            
            if pnl > 0:
                strategies[strategy]['wins'] += 1
            else:
                strategies[strategy]['losses'] += 1
        
        # Calculate win rates
        for strategy in strategies.values():
            if strategy['count'] > 0:
                strategy['win_rate'] = (strategy['wins'] / strategy['count']) * 100
        
        return strategies
    
    def get_summary(self) -> Dict:
        """Get comprehensive performance summary"""
        return {
            'total_trades': len(self.trades),
            'total_pnl': self.get_total_pnl(),
            'win_rate': self.get_win_rate(),
            'sharpe_ratio': self.get_sharpe_ratio(),
            'max_drawdown': self.get_max_drawdown(),
            'strategy_breakdown': self.get_strategy_performance()
        }
    
    def print_summary(self):
        """Print formatted performance summary"""
        summary = self.get_summary()
        
        print("\n" + "="*50)
        print("PERFORMANCE SUMMARY")
        print("="*50)
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Total P&L: ${summary['total_pnl']:.2f}")
        print(f"Win Rate: {summary['win_rate']:.1f}%")
        print(f"Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: ${summary['max_drawdown']:.2f}")
        
        print("\nStrategy Breakdown:")
        for strategy, stats in summary['strategy_breakdown'].items():
            print(f"\n  {strategy.upper()}:")
            print(f"    Trades: {stats['count']}")
            print(f"    P&L: ${stats['total_pnl']:.2f}")
            print(f"    Win Rate: {stats['win_rate']:.1f}%")
        print("="*50 + "\n")
