
**stakepd** is a Python package that extends [pandas](https://pandas.pydata.org/) with specialized tools for sports betting analytics. It provides custom DataFrame methods and utilities for modeling, analyzing, and simulating sports bets, odds, and outcomes.

## Features

- Sports betting-specific DataFrame extensions
- Odds conversion and normalization
- Bet simulation and bankroll management tools
- Integration with pandas workflows

## Installation

```bash
pip install stakepd
```

## Usage

```python
import pandas as pd
import stakepd

# Example: Calculate implied probabilities from odds
odds = pd.Series([2.0, 3.5, 1.8]) # A pandas Series of decimal odds
implied_probability = odds.implied_probability()
```

```python
print(implied_probability)
# Output:
# 0    0.500000
# 1    0.285714
# 2    0.555556
# dtype: float64
```

## Documentation

## License
