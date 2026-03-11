from typing import Dict, Optional, Tuple
from web3 import Web3
from eth_account import Account
import json

class DEXInterface:
    """Interface for interacting with DEXs"""
    
    UNISWAP_V2_ROUTER_ABI = [
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"}
            ],
            "name": "getAmountsOut",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                {"internalType": "address[]", "name": "path", "type": "address[]"},
                {"internalType": "address", "name": "to", "type": "address"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokens",
            "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    def __init__(self, w3: Web3, router_address: str):
        self.w3 = w3
        self.router = w3.eth.contract(
            address=Web3.to_checksum_address(router_address),
            abi=self.UNISWAP_V2_ROUTER_ABI
        )
    
    def get_price(self, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """Get output amount for a swap"""
        try:
            path = [
                Web3.to_checksum_address(token_in),
                Web3.to_checksum_address(token_out)
            ]
            amounts = self.router.functions.getAmountsOut(amount_in, path).call()
            return amounts[1] if len(amounts) > 1 else None
        except Exception as e:
            print(f"Error getting price: {e}")
            return None
    
    def calculate_price_impact(
        self, 
        token_in: str, 
        token_out: str, 
        amount_in: int
    ) -> Tuple[Optional[float], Optional[int]]:
        """Calculate price and price impact"""
        try:
            # Get price for small amount (reference)
            small_amount = 10 ** 18  # 1 token
            ref_out = self.get_price(token_in, token_out, small_amount)
            
            # Get price for actual amount
            actual_out = self.get_price(token_in, token_out, amount_in)
            
            if ref_out and actual_out:
                ref_price = ref_out / small_amount
                actual_price = actual_out / amount_in
                price_impact = ((ref_price - actual_price) / ref_price) * 100
                return price_impact, actual_out
            
            return None, None
        except Exception as e:
            print(f"Error calculating price impact: {e}")
            return None, None
    
    def build_swap_tx(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        amount_out_min: int,
        recipient: str,
        deadline: int
    ) -> Dict:
        """Build swap transaction"""
        path = [
            Web3.to_checksum_address(token_in),
            Web3.to_checksum_address(token_out)
        ]
        
        return self.router.functions.swapExactTokensForTokens(
            amount_in,
            amount_out_min,
            path,
            Web3.to_checksum_address(recipient),
            deadline
        ).build_transaction({
            'from': recipient,
            'gas': 250000,
            'gasPrice': self.w3.eth.gas_price
        })


class UniswapV2Interface(DEXInterface):
    """Uniswap V2 specific interface"""
    pass


class UniswapV3Interface:
    """Uniswap V3 specific interface (simplified)"""
    
    def __init__(self, w3: Web3, quoter_address: str):
        self.w3 = w3
        self.quoter_address = quoter_address
    
    def get_price(self, token_in: str, token_out: str, amount_in: int, fee: int = 3000) -> Optional[int]:
        """Get quote from Uniswap V3"""
        # Simplified - in production, use actual Quoter contract
        return None
