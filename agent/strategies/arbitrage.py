from typing import Dict, List, Optional
import asyncio
from web3 import Web3

class ArbitrageStrategy:
    """Detects and executes arbitrage opportunities across DEXs"""
    
    def __init__(self, w3: Web3, config: Dict):
        self.w3 = w3
        self.config = config
        self.min_profit = config.get("MIN_PROFIT_THRESHOLD", 0.5)
        
    async def find_opportunities(self, token_pairs: List[tuple]) -> List[Dict]:
        """Scan for arbitrage opportunities"""
        opportunities = []
        
        for token_a, token_b in token_pairs:
            # Get prices from different DEXs
            price_dex1 = await self._get_price(token_a, token_b, "uniswap_v2")
            price_dex2 = await self._get_price(token_a, token_b, "uniswap_v3")
            
            if price_dex1 and price_dex2:
                profit_pct = abs(price_dex1 - price_dex2) / min(price_dex1, price_dex2) * 100
                
                if profit_pct > self.min_profit:
                    opportunities.append({
                        "token_a": token_a,
                        "token_b": token_b,
                        "buy_dex": "uniswap_v2" if price_dex1 < price_dex2 else "uniswap_v3",
                        "sell_dex": "uniswap_v3" if price_dex1 < price_dex2 else "uniswap_v2",
                        "profit_pct": profit_pct,
                        "buy_price": min(price_dex1, price_dex2),
                        "sell_price": max(price_dex1, price_dex2)
                    })
        
        return opportunities
    
    async def _get_price(self, token_a: str, token_b: str, dex: str) -> Optional[float]:
        """Get token price from specific DEX"""
        try:
            # Implement actual price fetching logic here
            # This is a placeholder
            return 1.0
        except Exception as e:
            print(f"Error fetching price from {dex}: {e}")
            return None
    
    def calculate_optimal_amount(self, opportunity: Dict) -> float:
        """Calculate optimal trade amount considering gas and slippage"""
        max_position = self.config.get("MAX_POSITION_SIZE", 1000)
        
        # Simple calculation - can be enhanced with more sophisticated models
        profit_pct = opportunity["profit_pct"]
        optimal = max_position * (profit_pct / 10)
        
        return min(optimal, max_position)
