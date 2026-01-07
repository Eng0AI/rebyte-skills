# EdgarTools Objects Reference

## Core Objects Overview

| Object | Purpose | Typical Tokens |
|--------|---------|----------------|
| Company | Company entity & access | ~75 (context) |
| Filing | Single SEC filing | ~50 (context) |
| Filings | Collection of filings | ~95 (context) |
| XBRL | Structured financial data | ~275 (context) |
| Statement | Single financial statement | ~400 (context) |

---

## Company Object

### Creation
```python
from edgar import Company

# By ticker
company = Company("AAPL")

# By CIK
company = Company("0000320193")

# By name (fuzzy match)
company = Company("Apple Inc")
```

### Properties
```python
company.name           # "Apple Inc."
company.cik            # "0000320193"
company.tickers        # ["AAPL"]
company.sic            # "3571"
company.sic_description # "Electronic Computers"
company.industry       # Industry classification
company.state          # State of incorporation
company.exchanges      # ["NASDAQ"]
```

### Methods
```python
# Get filings
filings = company.get_filings()           # All filings
filings = company.get_filings(form="10-K") # Specific form

# Financial statements (Entity Facts API - fast)
income = company.income_statement(periods=4)
balance = company.balance_sheet(periods=4)
cashflow = company.cash_flow_statement(periods=4)

# Context for AI
company.to_context()  # Token-efficient summary
```

---

## Filing Object

### Access
```python
# From company
filing = company.get_filings(form="10-K").latest()

# From global search
from edgar import get_filings
filings = get_filings(form="10-K", year=2024)
filing = filings[0]
```

### Properties
```python
filing.form             # "10-K"
filing.filing_date      # datetime
filing.accession_number # "0000320193-24-000081"
filing.company          # Company name
filing.cik              # CIK number
```

### Methods
```python
# Summaries
filing.to_context()    # Token-efficient summary

# Full content (EXPENSIVE - 50K+ tokens)
filing.text()          # Plain text
filing.markdown()      # Markdown format

# Structured data
filing.xbrl()          # XBRL financial data
filing.items()         # Document sections

# Search within filing
filing.search("climate risk")  # Find text in document
```

---

## Filings Collection

### Filtering
```python
filings = company.get_filings()

# Filter by form
filings_10k = filings.filter(form="10-K")
filings_quarterly = filings.filter(form=["10-K", "10-Q"])

# Filter by date
filings_2024 = filings.filter(date="2024-01-01:")
filings_range = filings.filter(date="2023-01-01:2024-01-01")

# Get latest
latest = filings.latest()

# Get specific count
recent_5 = filings[:5]
```

### Properties
```python
len(filings)          # Count
filings.to_context()  # Summary for AI
```

---

## XBRL Object

### Access
```python
filing = company.get_filings(form="10-K").latest()
xbrl = filing.xbrl()
```

### Properties
```python
xbrl.statements       # Access to all statements
xbrl.facts            # Individual XBRL facts
xbrl.fiscal_year_end  # Fiscal year end date
xbrl.period_end       # Reporting period end
```

### Statements Access
```python
statements = xbrl.statements

# Core financial statements
income = statements.income_statement
balance = statements.balance_sheet
cashflow = statements.cash_flow_statement

# Other statements (if available)
equity = statements.stockholders_equity
comprehensive = statements.comprehensive_income
```

---

## Statement Object

### Display
```python
stmt = xbrl.statements.income_statement

# Print as ASCII table
print(stmt)

# Get as DataFrame
df = stmt.to_dataframe()
```

### Properties
```python
stmt.period           # Reporting period
stmt.line_items       # List of line items
```

### Line Item Access
```python
# Access specific metrics
revenue = stmt.get("Revenue")
net_income = stmt.get("NetIncome")
```

---

## MultiPeriodStatement Object

Returned by Entity Facts API methods:

```python
income = company.income_statement(periods=4)

# This is a MultiPeriodStatement
print(income)  # Shows 4 periods side-by-side

# Convert to DataFrame
df = income.to_dataframe()
```

---

## Token Optimization Guide

### Always Start with Context
```python
# GOOD - see what's available first
print(company.to_context())   # ~75 tokens
print(filing.to_context())    # ~50 tokens
print(xbrl.to_context())      # ~275 tokens

# Then drill down if needed
```

### Avoid Full Text Unless Necessary
```python
# BAD - expensive
text = filing.text()  # 50,000+ tokens

# GOOD - get what you need
xbrl = filing.xbrl()  # Structured data
income = xbrl.statements.income_statement  # ~400 tokens
```

### Use Entity Facts for Trends
```python
# GOOD - single API call, multiple periods
income = company.income_statement(periods=12)

# BAD - parsing 12 separate filings
for q in range(12):
    filing = filings[q]
    xbrl = filing.xbrl()  # 12 XBRL parses
```

---

## Documentation Access

Every object has `.docs` for built-in documentation:

```python
company.docs                      # Full docs
company.docs.search("revenue")    # Search docs

filing.docs
filing.docs.search("items")

xbrl.docs
xbrl.docs.search("statements")
```
