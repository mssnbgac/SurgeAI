// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
}

contract TradingAgent is Ownable, ReentrancyGuard {
    uint256 public agentId;
    address public identityRegistry;
    
    struct Trade {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 amountOut;
        uint256 timestamp;
        string strategy;
    }

    Trade[] public trades;
    mapping(address => bool) public authorizedExecutors;
    
    uint256 public totalProfit;
    uint256 public totalLoss;
    uint256 public tradeCount;

    event TradeExecuted(
        uint256 indexed tradeId,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut,
        string strategy
    );
    
    event ExecutorAuthorized(address indexed executor, bool authorized);
    event FundsDeposited(address indexed token, uint256 amount);
    event FundsWithdrawn(address indexed token, uint256 amount);

    modifier onlyAuthorized() {
        require(authorizedExecutors[msg.sender] || msg.sender == owner(), "Not authorized");
        _;
    }

    constructor(uint256 _agentId, address _identityRegistry) Ownable(msg.sender) {
        agentId = _agentId;
        identityRegistry = _identityRegistry;
        authorizedExecutors[msg.sender] = true;
    }

    function setExecutor(address executor, bool authorized) external onlyOwner {
        authorizedExecutors[executor] = authorized;
        emit ExecutorAuthorized(executor, authorized);
    }

    function deposit(address token, uint256 amount) external nonReentrant {
        require(IERC20(token).transferFrom(msg.sender, address(this), amount), "Transfer failed");
        emit FundsDeposited(token, amount);
    }

    function withdraw(address token, uint256 amount) external onlyOwner nonReentrant {
        require(IERC20(token).transfer(msg.sender, amount), "Transfer failed");
        emit FundsWithdrawn(token, amount);
    }

    function executeTrade(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut,
        address dexRouter,
        bytes calldata swapData,
        string calldata strategy
    ) external onlyAuthorized nonReentrant returns (uint256) {
        require(IERC20(tokenIn).balanceOf(address(this)) >= amountIn, "Insufficient balance");
        
        IERC20(tokenIn).approve(dexRouter, amountIn);
        
        uint256 balanceBefore = IERC20(tokenOut).balanceOf(address(this));
        (bool success, ) = dexRouter.call(swapData);
        require(success, "Swap failed");
        
        uint256 amountOut = IERC20(tokenOut).balanceOf(address(this)) - balanceBefore;
        require(amountOut >= minAmountOut, "Slippage too high");

        trades.push(Trade({
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            amountIn: amountIn,
            amountOut: amountOut,
            timestamp: block.timestamp,
            strategy: strategy
        }));

        tradeCount++;
        emit TradeExecuted(trades.length - 1, tokenIn, tokenOut, amountIn, amountOut, strategy);
        
        return amountOut;
    }

    function getTradeHistory() external view returns (Trade[] memory) {
        return trades;
    }

    function getBalance(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }

    function getPerformanceMetrics() external view returns (
        uint256 _tradeCount,
        uint256 _totalProfit,
        uint256 _totalLoss
    ) {
        return (tradeCount, totalProfit, totalLoss);
    }
}
