# Financial Skill - SEC Filing Analysis

A Claude Code skill for SEC filing analysis powered by [EdgarTools](https://github.com/dgunning/edgartools).

## Quick Start

### 1. Install EdgarTools

```bash
pip install edgartools
```

### 2. Set SEC Identity (Required)

```python
from edgar import set_identity
set_identity("Your Name your.email@example.com")
```

### 3. Start Analyzing

```python
from edgar import Company

company = Company("AAPL")
income = company.income_statement(periods=4)
print(income)
```

## What This Skill Enables

- Query SEC filings (10-K, 10-Q, 8-K, etc.)
- Extract financial statements (income, balance sheet, cash flow)
- Compare companies and track trends
- Monitor insider trading (Form 4)
- Track institutional holdings (13F)
- Analyze IPO registrations (S-1)

## Key Features

### Token-Efficient Design
Always use `.to_context()` first - saves 60-90% tokens vs full output.

### Three Filing Access Methods
1. **Published Filings** - Bulk cross-company analysis
2. **Current Filings** - Real-time monitoring
3. **Company Filings** - Single entity analysis

### Two Financial Data Methods
1. **Entity Facts API** - Fast multi-period trends
2. **Filing XBRL** - Detailed single-period analysis

## Example Queries

```
"Analyze Apple's revenue trend over the last 4 quarters"
"Compare Microsoft and Google's profit margins"
"Show me recent 8-K filings for Tesla"
"Find insider trading activity for NVDA"
"Get Amazon's latest 10-K financial statements"
```

## File Structure

```
financial-skill/
├── SKILL.md                    # Main skill definition
├── README.md                   # This file
├── requirements.txt            # Dependencies
└── reference/
    ├── workflows.md            # Common analysis workflows
    ├── objects.md              # Object reference
    └── form-types.md           # SEC form types guide
```

## Documentation

- [EdgarTools GitHub](https://github.com/dgunning/edgartools)
- [EdgarTools Documentation](https://dgunning.github.io/edgartools/)
- [SEC EDGAR](https://www.sec.gov/edgar)

## License

MIT (via EdgarTools dependency)
