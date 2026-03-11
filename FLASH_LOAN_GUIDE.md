# Flash Loan Quick Start Guide

## What You Need to Know

Flash loans let you borrow large amounts without collateral, execute trades, and repay within one transaction. Perfect for arbitrage!

## Quick Example

```python
# 1. Find arbitrage opportunity
opportunities = arbitrage.find_opportunities(token_pairs)

# 2. Check if flash loan is profitable
flash_opps = flash_loan.find_flash_loan_opportunities(
    opportunities,
    max_loan_amount=100000  # $100k
)

# 3. Simulate first
for opp in flash_opps:
    sim = flash_loan.simulate_flash_loan(opp)
    if sim['success']:
        print(f"Profit: ${sim['profit']:,.2f}")
        # Execute in production
```

## Profitability Check

```
Loan Amount: $50,000
Arbitrage Profit: 1.2% = $600
Flash Loan Fee: 0.09% = $45
Gas Cost: ~$20
Net Profit: $535 ✅
```

## Key Points

- ✅ No capital needed
- ✅ 0.09% fee (Aave V3)
- ✅ Must profit in single transaction
- ⚠️ High gas costs (300k-500k)
- ⚠️ Slippage can cause failures

## Integration

Already integrated in `main_production.py`:

```python
# Automatically checks for flash loan opportunities
flash_loan_opps = self.flash_loan.find_flash_loan_opportunities(
    opportunities,
    max_loan_amount=100000
)
```

## Stats

Monitor performance:

```python
stats = flash_loan.get_flash_loan_stats()
print(f"Success Rate: {stats['success_rate']:.1f}%")
print(f"Total Profit: ${stats['total_profit']:,.2f}")
```

## Next Steps

1. Deploy flash loan receiver contract (see `flash_loan.py`)
2. Test on testnet
3. Monitor logs for opportunities
4. Adjust `max_loan_amount` based on risk tolerance
