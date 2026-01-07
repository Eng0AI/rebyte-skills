# EdgarTools Workflows Reference

## Workflow 1: Compare Revenue Across Competitors

```python
from edgar import Company, set_identity

set_identity("Your Name email@example.com")

# Define competitors
competitors = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]

# Compare revenue trends
for ticker in competitors:
    company = Company(ticker)
    income = company.income_statement(periods=4)  # 4 quarters
    print(f"\n{'='*50}")
    print(f"{company.name} ({ticker})")
    print(f"{'='*50}")
    print(income)
```

---

## Workflow 2: Monitor Recent 10-K/10-Q Filings

```python
from edgar import get_current_filings, set_identity

set_identity("Your Name email@example.com")

# Get today's quarterly/annual reports
current = get_current_filings()

# Filter to 10-K and 10-Q only
earnings_filings = current.filter(form=["10-K", "10-Q"])

print(f"Found {len(earnings_filings)} earnings filings today:")
for filing in earnings_filings[:20]:
    print(f"  {filing.company} - {filing.form} - {filing.filing_date}")
```

---

## Workflow 3: Deep Dive Single Company Financials

```python
from edgar import Company, set_identity

set_identity("Your Name email@example.com")

company = Company("NVDA")

# Get latest 10-K
filing = company.get_filings(form="10-K").latest()
print(f"Analyzing: {filing.to_context()}")

# Get XBRL financial data
xbrl = filing.xbrl()

# Access all statements
statements = xbrl.statements

# Income Statement
print("\n=== INCOME STATEMENT ===")
print(statements.income_statement)

# Balance Sheet
print("\n=== BALANCE SHEET ===")
print(statements.balance_sheet)

# Cash Flow Statement
print("\n=== CASH FLOW STATEMENT ===")
print(statements.cash_flow_statement)
```

---

## Workflow 4: Extract Filing Sections (MD&A, Risk Factors)

```python
from edgar import Company, set_identity

set_identity("Your Name email@example.com")

company = Company("TSLA")
filing = company.get_filings(form="10-K").latest()

# Get document items/sections
items = filing.items()

# Common 10-K sections:
# Item 1 - Business
# Item 1A - Risk Factors
# Item 7 - MD&A (Management Discussion & Analysis)
# Item 8 - Financial Statements

# Access specific sections
for item in items:
    print(f"{item.name}: {len(item.text)} characters")
```

---

## Workflow 5: Historical IPO Analysis

```python
from edgar import get_filings, set_identity

set_identity("Your Name email@example.com")

# Find S-1 filings (IPO registrations) from 2024
s1_filings = get_filings(form="S-1", year=2024)

print(f"Found {len(s1_filings)} S-1 filings in 2024")

# List recent IPO registrations
for filing in s1_filings[:15]:
    print(f"{filing.company} - Filed: {filing.filing_date}")
```

---

## Workflow 6: 5-Year Financial Trend Analysis

```python
from edgar import Company, set_identity

set_identity("Your Name email@example.com")

company = Company("AMZN")

# Get 5 years of data (20 quarters)
print("=== 5-YEAR INCOME STATEMENT ===")
income = company.income_statement(periods=20)
print(income)

print("\n=== 5-YEAR BALANCE SHEET ===")
balance = company.balance_sheet(periods=20)
print(balance)

print("\n=== 5-YEAR CASH FLOW ===")
cashflow = company.cash_flow_statement(periods=20)
print(cashflow)
```

---

## Workflow 7: Track Insider Trading Activity

```python
from edgar import Company, set_identity

set_identity("Your Name email@example.com")

company = Company("AAPL")

# Form 4 = Insider trading reports
insider_filings = company.get_filings(form="4")

print(f"Recent insider transactions for {company.name}:")
for filing in insider_filings[:10]:
    print(f"  {filing.filing_date}: {filing.to_context()}")
```

---

## Workflow 8: Institutional Holdings (13F)

```python
from edgar import get_filings, set_identity

set_identity("Your Name email@example.com")

# 13F = Institutional investment manager holdings
# Filed quarterly by funds with >$100M AUM

filings_13f = get_filings(form="13F-HR", year=2024, quarter=3)

print(f"Found {len(filings_13f)} 13F filings for Q3 2024")

# Look at specific fund
for filing in filings_13f[:10]:
    print(f"{filing.company}: Filed {filing.filing_date}")
```

---

## Workflow 9: Compare Companies Side-by-Side

```python
from edgar import Company, set_identity

set_identity("Your Name email@example.com")

def get_key_metrics(ticker):
    """Extract key financial metrics for a company."""
    company = Company(ticker)
    income = company.income_statement(periods=4)
    balance = company.balance_sheet(periods=1)

    return {
        "ticker": ticker,
        "name": company.name,
        "industry": company.industry,
        # Add specific metrics from statements
    }

# Compare chip companies
tickers = ["NVDA", "AMD", "INTC"]
for ticker in tickers:
    metrics = get_key_metrics(ticker)
    print(f"\n{metrics['name']} ({ticker})")
    print(f"  Industry: {metrics['industry']}")
```

---

## Error Handling Patterns

```python
from edgar import Company, set_identity

set_identity("Your Name email@example.com")

def safe_get_financials(ticker):
    """Safely retrieve financials with error handling."""
    try:
        company = Company(ticker)
    except Exception as e:
        print(f"Could not find company: {ticker}")
        return None

    filings = company.get_filings(form="10-K")
    if len(filings) == 0:
        print(f"No 10-K filings for {ticker}")
        return None

    try:
        filing = filings.latest()
        xbrl = filing.xbrl()
        return xbrl.statements
    except Exception as e:
        print(f"Could not parse XBRL for {ticker}: {e}")
        return None

# Usage
statements = safe_get_financials("AAPL")
if statements:
    print(statements.income_statement)
```

---

## Performance Optimization

```python
from edgar import Company, get_filings, set_identity

set_identity("Your Name email@example.com")

# TIP 1: Use Entity Facts API for trends (faster than parsing filings)
company = Company("MSFT")
income = company.income_statement(periods=12)  # 12 quarters, single API call

# TIP 2: Filter early, retrieve late
filings = get_filings(form="10-K", year=2024)  # Pre-filtered
# vs
# filings = get_filings()  # All filings, then filter - SLOW

# TIP 3: Use .to_context() before diving deep
filing = company.get_filings(form="10-K").latest()
print(filing.to_context())  # ~50 tokens, see what's available
# Only then: filing.text() if you really need full text

# TIP 4: Batch company lookups
tickers = ["AAPL", "MSFT", "GOOGL"]
companies = [Company(t) for t in tickers]  # Load all at once
```
