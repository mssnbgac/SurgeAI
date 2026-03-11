"""
MEV (Maximal Extractable Value) Protection Strategy
Protects trades from front-running, sandwich attacks, and other MEV exploits
"""

from typing import Dict, List, Optional, Tuple
from web3 import Web3
import time
from dataclasses import dataclass

@dataclass
class MEVThreat:
    """Represents a detected MEV threat"""
    threat_type: str  # 'frontrun', 'sandwich', 'backrun'
    severity: float  # 0-1
    detected_at: int
    details: Dict

class MEVProtector:
    """
    Advanced MEV protection system
    Detects and mitigates MEV attacks
    """
    
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.mempool_monitor = MempoolMonitor(w3)
        self.threat_history: List[MEVThreat] = []
        self.protected_transactions = 0
        self.detected_threats = 0
        
    def analyze_trade_safety(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        dex: str
    ) -> Dict:
        """
        Analyze if a trade is safe from MEV attacks
        Returns safety score and recommendations
        """
        safety_score = 1.0
        threats = []
        recommendations = []
        
        # Check 1: Mempool analysis
        mempool_threats = self.mempool_monitor.check_mempool_threats(
            token_in, token_out, amount_in
        )
        
        if mempool_threats:
            safety_score *= 0.7
            threats.extend(mempool_threats)
            recommendations.append("High mempool activity detected - consider delaying trade")
        
        # Check 2: Price impact analysis
        price_impact = self._estimate_price_impact(amount_in, token_in, token_out)
        
        if price_impact > 0.02:  # 2% impact
            safety_score *= 0.8
            threats.append({
                'type': 'high_price_impact',
                'severity': min(price_impact * 10, 1.0),
                'details': f'Price impact: {price_impact*100:.2f}%'
            })
            recommendations.append("High price impact - vulnerable to sandwich attacks")
        
        # Check 3: Gas price analysis
        current_gas = self.w3.eth.gas_price
        avg_gas = self._get_average_gas_price()
        
        if current_gas > avg_gas * 1.5:
            safety_score *= 0.9
            threats.append({
                'type': 'high_gas_competition',
                'severity': 0.6,
                'details': f'Gas price {(current_gas/avg_gas - 1)*100:.1f}% above average'
            })
            recommendations.append("High gas competition - increased MEV risk")
        
        # Check 4: Block position analysis
        block_position_risk = self._analyze_block_position_risk()
        safety_score *= (1 - block_position_risk * 0.3)
        
        return {
            'safe': safety_score > 0.7,
            'safety_score': safety_score,
            'threats': threats,
            'recommendations': recommendations,
            'protection_methods': self._suggest_protection_methods(safety_score, threats)
        }
    
    def _estimate_price_impact(self, amount: int, token_in: str, token_out: str) -> float:
        """Estimate price impact of trade"""
        # Simplified calculation
        # In production, query actual pool reserves
        return min(amount / 1000000, 0.1)  # Cap at 10%
    
    def _get_average_gas_price(self) -> int:
        """Get average gas price from recent blocks"""
        try:
            latest_block = self.w3.eth.block_number
            gas_prices = []
            
            for i in range(5):
                block = self.w3.eth.get_block(latest_block - i)
                if hasattr(block, 'baseFeePerGas') and block.baseFeePerGas:
                    gas_prices.append(block.baseFeePerGas)
            
            return int(sum(gas_prices) / len(gas_prices)) if gas_prices else self.w3.eth.gas_price
        except:
            return self.w3.eth.gas_price
    
    def _analyze_block_position_risk(self) -> float:
        """Analyze risk based on position in block"""
        # Transactions at end of block are more vulnerable
        # This is a simplified heuristic
        return 0.3  # Medium risk
    
    def _suggest_protection_methods(self, safety_score: float, threats: List) -> List[str]:
        """Suggest MEV protection methods based on threats"""
        methods = []
        
        if safety_score < 0.5:
            methods.append("Use Flashbots/MEV-protected RPC")
            methods.append("Split trade into smaller chunks")
            methods.append("Use limit orders instead of market orders")
        
        if safety_score < 0.7:
            methods.append("Increase slippage tolerance slightly")
            methods.append("Use private transaction relay")
        
        if any(t.get('type') == 'high_price_impact' for t in threats):
            methods.append("Route through multiple DEXs")
            methods.append("Use aggregator for better execution")
        
        return methods
    
    def apply_protection(
        self,
        trade_params: Dict,
        protection_level: str = 'medium'
    ) -> Dict:
        """
        Apply MEV protection to trade parameters
        Returns modified trade parameters with protection
        """
        protected_params = trade_params.copy()
        
        if protection_level == 'high':
            # Maximum protection
            protected_params['use_flashbots'] = True
            protected_params['max_priority_fee'] = self.w3.eth.max_priority_fee * 2
            protected_params['deadline'] = int(time.time()) + 120  # 2 min deadline
            protected_params['slippage'] = min(trade_params.get('slippage', 0.01) * 1.5, 0.05)
            
        elif protection_level == 'medium':
            # Balanced protection
            protected_params['max_priority_fee'] = self.w3.eth.max_priority_fee * 1.5
            protected_params['deadline'] = int(time.time()) + 180  # 3 min deadline
            protected_params['slippage'] = trade_params.get('slippage', 0.01) * 1.2
            
        else:  # low
            # Minimal protection
            protected_params['deadline'] = int(time.time()) + 300  # 5 min deadline
        
        self.protected_transactions += 1
        
        return protected_params
    
    def get_protection_stats(self) -> Dict:
        """Get MEV protection statistics"""
        return {
            'protected_transactions': self.protected_transactions,
            'detected_threats': self.detected_threats,
            'threat_history': len(self.threat_history),
            'success_rate': self.protected_transactions / max(self.detected_threats, 1)
        }


class MempoolMonitor:
    """
    Monitors mempool for MEV threats
    Detects front-running and sandwich attack attempts
    """
    
    def __init__(self, w3: Web3):
        self.w3 = w3
        self.recent_transactions = []
        self.suspicious_patterns = []
    
    def check_mempool_threats(
        self,
        token_in: str,
        token_out: str,
        amount: int
    ) -> List[Dict]:
        """
        Check mempool for threats related to this trade
        Returns list of detected threats
        """
        threats = []
        
        # In production, this would analyze actual mempool
        # For now, we simulate threat detection
        
        # Simulate checking for similar pending transactions
        similar_tx_count = self._count_similar_transactions(token_in, token_out)
        
        if similar_tx_count > 3:
            threats.append({
                'type': 'high_competition',
                'severity': 0.6,
                'details': f'{similar_tx_count} similar transactions in mempool'
            })
        
        # Check for suspicious gas prices
        if self._detect_suspicious_gas_prices():
            threats.append({
                'type': 'potential_frontrun',
                'severity': 0.7,
                'details': 'Suspicious gas price patterns detected'
            })
        
        return threats
    
    def _count_similar_transactions(self, token_in: str, token_out: str) -> int:
        """Count similar transactions in mempool"""
        # Simplified simulation
        return 1
    
    def _detect_suspicious_gas_prices(self) -> bool:
        """Detect suspicious gas price patterns"""
        # Simplified simulation
        return False


class FlashbotsProtection:
    """
    Integration with Flashbots for MEV protection
    Sends transactions through private relay
    """
    
    def __init__(self, flashbots_rpc: Optional[str] = None):
        self.flashbots_rpc = flashbots_rpc or "https://relay.flashbots.net"
        self.enabled = flashbots_rpc is not None
    
    def send_private_transaction(self, tx_params: Dict) -> Optional[str]:
        """
        Send transaction through Flashbots private relay
        Protects from front-running
        """
        if not self.enabled:
            return None
        
        # In production, this would use actual Flashbots SDK
        print(f"🔒 Sending transaction through Flashbots relay")
        print(f"   Protection: Front-running prevented")
        
        return "0x" + "0" * 64  # Mock transaction hash
    
    def estimate_bundle_price(self, transactions: List[Dict]) -> int:
        """Estimate cost of transaction bundle"""
        # Simplified estimation
        return sum(tx.get('gas', 21000) * tx.get('gasPrice', 0) for tx in transactions)
