from typing import Dict, List
import numpy as np

class RiskManager:
    """Manages portfolio risk and implements protection strategies"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_position_size = config.get("MAX_POSITION_SIZE", 1000)
        self.stop_loss_pct = 5.0  # 5% stop loss
        self.take_profit_pct = 10.0  # 10% take profit
        
    def check_position_limits(self, position: Dict) -> bool:
        """Check if position is within risk limits"""
        return position["amount"] <= self.max_position_size
    
    def calculate_stop_loss(self, entry_price: float) -> float:
        """Calculate stop loss price"""
        return entry_price * (1 - self.stop_loss_pct / 100)
    
    def calculate_take_profit(self, entry_price: float) -> float:
        """Calculate take profit price"""
        return entry_price * (1 + self.take_profit_pct / 100)
    
    def should_exit_position(self, position: Dict, current_price: float) -> Dict:
        """Determine if position should be exited"""
        entry_price = position["entry_price"]
        pnl_pct = ((current_price - entry_price) / entry_price) * 100
        
        if pnl_pct <= -self.stop_loss_pct:
            return {
                "should_exit": True,
                "reason": "stop_loss",
                "pnl_pct": pnl_pct
            }
        
        if pnl_pct >= self.take_profit_pct:
            return {
                "should_exit": True,
                "reason": "take_profit",
                "pnl_pct": pnl_pct
            }
        
        return {"should_exit": False, "pnl_pct": pnl_pct}
    
    def calculate_portfolio_risk(self, positions: List[Dict]) -> Dict:
        """Calculate overall portfolio risk metrics"""
        if not positions:
            return {"total_exposure": 0, "risk_score": 0}
        
        total_value = sum(p["amount"] * p.get("current_price", p["entry_price"]) for p in positions)
        
        # Simple risk score based on concentration
        max_position = max(p["amount"] for p in positions)
        concentration = max_position / total_value if total_value > 0 else 0
        
        return {
            "total_exposure": total_value,
            "position_count": len(positions),
            "concentration": concentration,
            "risk_score": concentration * 100  # 0-100 scale
        }
    
    def get_position_size_recommendation(self, opportunity: Dict, portfolio_value: float) -> float:
        """Recommend position size based on risk parameters"""
        # Kelly Criterion simplified
        win_rate = 0.6  # Assume 60% win rate
        avg_win = opportunity.get("profit_pct", 5) / 100
        avg_loss = self.stop_loss_pct / 100
        
        kelly = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
        kelly = max(0, min(kelly, 0.25))  # Cap at 25% of portfolio
        
        recommended = portfolio_value * kelly
        return min(recommended, self.max_position_size)
