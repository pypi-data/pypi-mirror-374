# PivotalPath

The industry standard for hedge fund indices data and analytics.

## Installation

```bash
pip install pivotalpath
```

## Quick Start

```python
import pivotalpath as pp

# See available tickers
print(pp.examples.example1())

# Get fund returns
returns = pp.get_returns("PP-HFC")

# Calculate performance stats
stats = pp.get_stats(target="PP-HFC", base="SP500", stat="sharpe")
```

## Features

- Comprehensive hedge fund performance analytics
- 20+ institutional-quality metrics
- Real-time data API integration  
- LLM-optimized for AI integration

## License

MIT
