"""
Automated Strategy Optimization using Reinforcement Learning and Genetic Algorithms
Continuously tunes strategy parameters for optimal performance
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


@dataclass
class StrategyParameters:
    """Container for strategy parameters"""
    min_profit_threshold: float
    max_position_size: float
    slippage_tolerance: float
    stop_loss_pct: float
    take_profit_pct: float
    risk_score_threshold: float
    
    def to_dict(self) -> Dict:
        return {
            'min_profit_threshold': self.min_profit_threshold,
            'max_position_size': self.max_position_size,
            'slippage_tolerance': self.slippage_tolerance,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct,
            'risk_score_threshold': self.risk_score_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


class StrategyOptimizer:
    """
    Automated strategy parameter optimization using:
    - Genetic algorithms for parameter search
    - Reinforcement learning for adaptive tuning
    - Bayesian optimization for efficient exploration
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Current best parameters
        self.best_params = StrategyParameters(
            min_profit_threshold=config.get('MIN_PROFIT_THRESHOLD', 0.5),
            max_position_size=config.get('MAX_POSITION_SIZE', 1000),
            slippage_tolerance=config.get('SLIPPAGE_TOLERANCE', 0.01),
            stop_loss_pct=5.0,
            take_profit_pct=10.0,
            risk_score_threshold=70.0
        )
        
        # Optimization history
        self.optimization_history: List[Dict] = []
        self.performance_history: List[Dict] = []
        
        # Genetic algorithm population
        self.population_size = 20
        self.population: List[StrategyParameters] = []
        self.generation = 0
        
        # Reinforcement learning state
        self.learning_rate = 0.01
        self.exploration_rate = 0.2
        self.discount_factor = 0.95
        
        # Performance tracking
        self.best_fitness = -float('inf')
        self.optimization_runs = 0
        
        logger.info("Strategy Optimizer initialized")
    
    def optimize_parameters(
        self,
        performance_data: List[Dict],
        method: str = 'genetic'
    ) -> StrategyParameters:
        """
        Optimize strategy parameters based on historical performance
        
        Args:
            performance_data: List of trade results with parameters used
            method: 'genetic', 'reinforcement', or 'bayesian'
            
        Returns:
            Optimized strategy parameters
        """
        logger.info(f"Starting parameter optimization using {method} method")
        
        if method == 'genetic':
            optimized = self._genetic_algorithm_optimization(performance_data)
        elif method == 'reinforcement':
            optimized = self._reinforcement_learning_optimization(performance_data)
        elif method == 'bayesian':
            optimized = self._bayesian_optimization(performance_data)
        else:
            logger.warning(f"Unknown method {method}, using genetic algorithm")
            optimized = self._genetic_algorithm_optimization(performance_data)
        
        # Update best parameters if improved
        fitness = self._calculate_fitness(optimized, performance_data)
        if fitness > self.best_fitness:
            self.best_params = optimized
            self.best_fitness = fitness
            logger.info(f"New best parameters found! Fitness: {fitness:.4f}")
        
        self.optimization_runs += 1
        self._record_optimization(optimized, fitness, method)
        
        return optimized
    
    def _genetic_algorithm_optimization(
        self,
        performance_data: List[Dict]
    ) -> StrategyParameters:
        """
        Use genetic algorithm to evolve optimal parameters
        """
        logger.info("Running genetic algorithm optimization...")
        
        # Initialize population if empty
        if not self.population:
            self.population = self._initialize_population()
        
        # Run evolution for multiple generations
        num_generations = 10
        
        for gen in range(num_generations):
            # Evaluate fitness for each individual
            fitness_scores = [
                self._calculate_fitness(params, performance_data)
                for params in self.population
            ]
            
            # Selection: keep top performers
            sorted_indices = np.argsort(fitness_scores)[::-1]
            elite_size = self.population_size // 4
            elite = [self.population[i] for i in sorted_indices[:elite_size]]
            
            # Crossover and mutation to create new generation
            new_population = elite.copy()
            
            while len(new_population) < self.population_size:
                # Select parents
                parent1 = elite[np.random.randint(0, elite_size)]
                parent2 = elite[np.random.randint(0, elite_size)]
                
                # Crossover
                child = self._crossover(parent1, parent2)
                
                # Mutation
                child = self._mutate(child)
                
                new_population.append(child)
            
            self.population = new_population
            self.generation += 1
            
            best_fitness = max(fitness_scores)
            logger.info(f"Generation {self.generation}: Best fitness = {best_fitness:.4f}")
        
        # Return best individual from final population
        final_fitness = [
            self._calculate_fitness(params, performance_data)
            for params in self.population
        ]
        best_idx = np.argmax(final_fitness)
        
        return self.population[best_idx]
    
    def _initialize_population(self) -> List[StrategyParameters]:
        """Initialize random population for genetic algorithm"""
        population = []
        
        for _ in range(self.population_size):
            params = StrategyParameters(
                min_profit_threshold=np.random.uniform(0.1, 2.0),
                max_position_size=np.random.uniform(500, 5000),
                slippage_tolerance=np.random.uniform(0.005, 0.05),
                stop_loss_pct=np.random.uniform(2.0, 10.0),
                take_profit_pct=np.random.uniform(5.0, 20.0),
                risk_score_threshold=np.random.uniform(50.0, 90.0)
            )
            population.append(params)
        
        return population
    
    def _crossover(
        self,
        parent1: StrategyParameters,
        parent2: StrategyParameters
    ) -> StrategyParameters:
        """Crossover two parent parameters to create child"""
        # Uniform crossover: randomly select from each parent
        return StrategyParameters(
            min_profit_threshold=(
                parent1.min_profit_threshold if np.random.random() > 0.5
                else parent2.min_profit_threshold
            ),
            max_position_size=(
                parent1.max_position_size if np.random.random() > 0.5
                else parent2.max_position_size
            ),
            slippage_tolerance=(
                parent1.slippage_tolerance if np.random.random() > 0.5
                else parent2.slippage_tolerance
            ),
            stop_loss_pct=(
                parent1.stop_loss_pct if np.random.random() > 0.5
                else parent2.stop_loss_pct
            ),
            take_profit_pct=(
                parent1.take_profit_pct if np.random.random() > 0.5
                else parent2.take_profit_pct
            ),
            risk_score_threshold=(
                parent1.risk_score_threshold if np.random.random() > 0.5
                else parent2.risk_score_threshold
            )
        )
    
    def _mutate(
        self,
        params: StrategyParameters,
        mutation_rate: float = 0.2
    ) -> StrategyParameters:
        """Apply random mutations to parameters"""
        if np.random.random() < mutation_rate:
            params.min_profit_threshold *= np.random.uniform(0.8, 1.2)
            params.min_profit_threshold = max(0.1, min(5.0, params.min_profit_threshold))
        
        if np.random.random() < mutation_rate:
            params.max_position_size *= np.random.uniform(0.8, 1.2)
            params.max_position_size = max(100, min(10000, params.max_position_size))
        
        if np.random.random() < mutation_rate:
            params.slippage_tolerance *= np.random.uniform(0.8, 1.2)
            params.slippage_tolerance = max(0.001, min(0.1, params.slippage_tolerance))
        
        if np.random.random() < mutation_rate:
            params.stop_loss_pct *= np.random.uniform(0.8, 1.2)
            params.stop_loss_pct = max(1.0, min(20.0, params.stop_loss_pct))
        
        if np.random.random() < mutation_rate:
            params.take_profit_pct *= np.random.uniform(0.8, 1.2)
            params.take_profit_pct = max(2.0, min(50.0, params.take_profit_pct))
        
        if np.random.random() < mutation_rate:
            params.risk_score_threshold *= np.random.uniform(0.9, 1.1)
            params.risk_score_threshold = max(30.0, min(95.0, params.risk_score_threshold))
        
        return params
    
    def _reinforcement_learning_optimization(
        self,
        performance_data: List[Dict]
    ) -> StrategyParameters:
        """
        Use reinforcement learning to adapt parameters based on rewards
        """
        logger.info("Running reinforcement learning optimization...")
        
        # Current state (parameters)
        current_params = self.best_params
        
        # Calculate current performance (reward)
        current_reward = self._calculate_fitness(current_params, performance_data)
        
        # Exploration vs exploitation
        if np.random.random() < self.exploration_rate:
            # Explore: try random variations
            new_params = self._mutate(current_params, mutation_rate=0.3)
        else:
            # Exploit: make small improvements
            new_params = self._gradient_step(current_params, performance_data)
        
        # Calculate new reward
        new_reward = self._calculate_fitness(new_params, performance_data)
        
        # Update if improved
        if new_reward > current_reward:
            logger.info(f"RL improvement: {current_reward:.4f} -> {new_reward:.4f}")
            return new_params
        else:
            # Decay exploration rate
            self.exploration_rate *= 0.99
            return current_params
    
    def _gradient_step(
        self,
        params: StrategyParameters,
        performance_data: List[Dict]
    ) -> StrategyParameters:
        """
        Take gradient step to improve parameters
        """
        # Calculate numerical gradient
        epsilon = 0.01
        current_fitness = self._calculate_fitness(params, performance_data)
        
        # Adjust each parameter slightly
        new_params = StrategyParameters(
            min_profit_threshold=params.min_profit_threshold * (1 + self.learning_rate),
            max_position_size=params.max_position_size,
            slippage_tolerance=params.slippage_tolerance,
            stop_loss_pct=params.stop_loss_pct * (1 - self.learning_rate * 0.5),
            take_profit_pct=params.take_profit_pct * (1 + self.learning_rate * 0.5),
            risk_score_threshold=params.risk_score_threshold
        )
        
        return new_params
    
    def _bayesian_optimization(
        self,
        performance_data: List[Dict]
    ) -> StrategyParameters:
        """
        Use Bayesian optimization for efficient parameter search
        """
        logger.info("Running Bayesian optimization...")
        
        # Simplified Bayesian optimization
        # In production, use libraries like scikit-optimize
        
        # Sample points around current best
        num_samples = 10
        samples = []
        
        for _ in range(num_samples):
            sample = self._mutate(self.best_params, mutation_rate=0.15)
            fitness = self._calculate_fitness(sample, performance_data)
            samples.append((sample, fitness))
        
        # Select best sample
        best_sample = max(samples, key=lambda x: x[1])
        
        return best_sample[0]
    
    def _calculate_fitness(
        self,
        params: StrategyParameters,
        performance_data: List[Dict]
    ) -> float:
        """
        Calculate fitness score for parameter set
        Higher is better
        """
        if not performance_data:
            return 0.0
        
        # Simulate performance with these parameters
        total_profit = 0
        total_trades = 0
        winning_trades = 0
        max_drawdown = 0
        cumulative = 0
        peak = 0
        
        for trade in performance_data:
            # Check if trade would have been taken with these params
            profit_pct = trade.get('profit_pct', 0)
            
            if abs(profit_pct) < params.min_profit_threshold:
                continue  # Would skip this trade
            
            total_trades += 1
            pnl = trade.get('pnl', 0)
            total_profit += pnl
            
            if pnl > 0:
                winning_trades += 1
            
            # Track drawdown
            cumulative += pnl
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        if total_trades == 0:
            return 0.0
        
        # Calculate metrics
        win_rate = winning_trades / total_trades
        avg_profit = total_profit / total_trades
        
        # Fitness function: balance profit, win rate, and risk
        fitness = (
            avg_profit * 0.4 +  # Profit weight
            win_rate * 100 * 0.3 +  # Win rate weight
            -max_drawdown * 0.2 +  # Drawdown penalty
            total_trades * 0.1  # Activity bonus
        )
        
        return fitness
    
    def adaptive_parameter_adjustment(
        self,
        recent_performance: List[Dict],
        market_conditions: Dict
    ) -> StrategyParameters:
        """
        Adaptively adjust parameters based on recent performance
        and current market conditions
        """
        logger.info("Performing adaptive parameter adjustment...")
        
        current = self.best_params
        
        # Analyze recent performance
        if len(recent_performance) < 5:
            return current
        
        recent_trades = recent_performance[-10:]
        win_rate = sum(1 for t in recent_trades if t.get('pnl', 0) > 0) / len(recent_trades)
        avg_profit = np.mean([t.get('pnl', 0) for t in recent_trades])
        
        # Adjust based on performance
        adjusted = StrategyParameters(
            min_profit_threshold=current.min_profit_threshold,
            max_position_size=current.max_position_size,
            slippage_tolerance=current.slippage_tolerance,
            stop_loss_pct=current.stop_loss_pct,
            take_profit_pct=current.take_profit_pct,
            risk_score_threshold=current.risk_score_threshold
        )
        
        # If losing streak, tighten parameters
        if win_rate < 0.4:
            adjusted.min_profit_threshold *= 1.2
            adjusted.stop_loss_pct *= 0.8
            adjusted.risk_score_threshold *= 1.1
            logger.info("Tightening parameters due to low win rate")
        
        # If winning streak, slightly loosen
        elif win_rate > 0.7:
            adjusted.min_profit_threshold *= 0.95
            adjusted.max_position_size *= 1.1
            logger.info("Loosening parameters due to high win rate")
        
        # Adjust for market volatility
        volatility = market_conditions.get('volatility', 0.02)
        if volatility > 0.05:  # High volatility
            adjusted.slippage_tolerance *= 1.3
            adjusted.stop_loss_pct *= 1.2
            logger.info("Adjusting for high market volatility")
        
        return adjusted
    
    def _record_optimization(
        self,
        params: StrategyParameters,
        fitness: float,
        method: str
    ):
        """Record optimization result"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'method': method,
            'generation': self.generation,
            'fitness': fitness,
            'parameters': params.to_dict()
        }
        self.optimization_history.append(record)
    
    def get_optimization_stats(self) -> Dict:
        """Get optimization statistics"""
        return {
            'optimization_runs': self.optimization_runs,
            'current_generation': self.generation,
            'best_fitness': self.best_fitness,
            'best_parameters': self.best_params.to_dict(),
            'exploration_rate': self.exploration_rate,
            'history_length': len(self.optimization_history)
        }
    
    def save_optimization_state(self, filepath: str = "optimization_state.json"):
        """Save optimization state to file"""
        state = {
            'best_params': self.best_params.to_dict(),
            'best_fitness': self.best_fitness,
            'generation': self.generation,
            'optimization_runs': self.optimization_runs,
            'exploration_rate': self.exploration_rate,
            'history': self.optimization_history[-100:]  # Last 100 records
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Optimization state saved to {filepath}")
    
    def load_optimization_state(self, filepath: str = "optimization_state.json"):
        """Load optimization state from file"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.best_params = StrategyParameters.from_dict(state['best_params'])
            self.best_fitness = state['best_fitness']
            self.generation = state['generation']
            self.optimization_runs = state['optimization_runs']
            self.exploration_rate = state['exploration_rate']
            self.optimization_history = state.get('history', [])
            
            logger.info(f"Optimization state loaded from {filepath}")
        except FileNotFoundError:
            logger.warning(f"No optimization state file found at {filepath}")
