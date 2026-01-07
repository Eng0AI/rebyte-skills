# SEC Form Types Reference

## Most Common Forms

### Annual & Quarterly Reports

| Form | Description | When Filed | Key Content |
|------|-------------|------------|-------------|
| **10-K** | Annual report | Within 60-90 days of fiscal year end | Full financials, business description, risk factors, MD&A |
| **10-Q** | Quarterly report | Within 40-45 days of quarter end | Quarterly financials, updates |
| **20-F** | Foreign annual report | Non-US companies | Same as 10-K for foreign filers |

### Current Events

| Form | Description | When Filed | Key Content |
|------|-------------|------------|-------------|
| **8-K** | Current report | Within 4 business days of event | Material events: M&A, exec changes, earnings |
| **6-K** | Foreign current report | As needed | Same as 8-K for foreign filers |

### Proxy & Governance

| Form | Description | When Filed | Key Content |
|------|-------------|------------|-------------|
| **DEF 14A** | Definitive proxy | Before shareholder meeting | Executive comp, board nominees, proposals |
| **DEFA14A** | Additional proxy materials | As needed | Supplemental proxy info |
| **PRE 14A** | Preliminary proxy | Before DEF 14A | Draft proxy for SEC review |

### Insider & Institutional Ownership

| Form | Description | When Filed | Key Content |
|------|-------------|------------|-------------|
| **4** | Insider trading | Within 2 business days | Officer/director stock transactions |
| **3** | Initial ownership | Within 10 days of becoming insider | Initial holdings disclosure |
| **5** | Annual ownership | Within 45 days of fiscal year end | Changes not reported on Form 4 |
| **13F** | Institutional holdings | Quarterly | Holdings of funds with >$100M AUM |
| **13D** | Beneficial ownership >5% | Within 10 days | Activist investors, large stakes |
| **13G** | Passive ownership >5% | Annual or within 45 days | Passive large shareholders |
| **SC 13D/A** | Amendments to 13D | As needed | Updates to 13D |

### Registration & Offerings

| Form | Description | When Filed | Key Content |
|------|-------------|------------|-------------|
| **S-1** | IPO registration | Before going public | Full company disclosure for IPO |
| **S-3** | Shelf registration | For follow-on offerings | Existing public companies |
| **S-4** | M&A registration | For stock-based M&A | Merger/acquisition details |
| **424B** | Prospectus | With offering | Final offering terms |
| **F-1** | Foreign IPO | Non-US company IPO | Same as S-1 for foreign filers |

### Other Important Forms

| Form | Description | When Filed | Key Content |
|------|-------------|------------|-------------|
| **11-K** | Employee benefit plans | Annual | 401k and benefit plan reports |
| **NT 10-K/Q** | Late filing notice | When filing will be late | Notification of delay |
| **8-A** | Securities registration | To register a class of securities | Exchange registration |

---

## Form Categories for Filtering

### Earnings/Financial Analysis
```python
filings = get_filings(form=["10-K", "10-Q"])
```

### Material Events
```python
filings = get_filings(form="8-K")
```

### Insider Activity
```python
filings = get_filings(form=["3", "4", "5"])
```

### Institutional Holdings
```python
filings = get_filings(form=["13F-HR", "13D", "13G"])
```

### IPO/Offerings
```python
filings = get_filings(form=["S-1", "S-1/A", "424B"])
```

### Proxy/Governance
```python
filings = get_filings(form=["DEF 14A", "DEFA14A"])
```

---

## Filing Timing Reference

| Form | Deadline | Large Accelerated | Accelerated | Non-Accelerated |
|------|----------|-------------------|-------------|-----------------|
| 10-K | After fiscal year | 60 days | 75 days | 90 days |
| 10-Q | After quarter | 40 days | 40 days | 45 days |
| 8-K | After event | 4 business days | 4 business days | 4 business days |

**Filer Categories:**
- **Large Accelerated**: >$700M public float
- **Accelerated**: $75M-$700M public float
- **Non-Accelerated**: <$75M public float

---

## Common Use Cases by Form

### Due Diligence on a Company
```python
# Comprehensive view
forms = ["10-K", "10-Q", "8-K", "DEF 14A"]
filings = company.get_filings(form=forms)
```

### Track Insider Sentiment
```python
# Watch for insider buying/selling
insider_forms = ["3", "4", "5"]
filings = company.get_filings(form=insider_forms)
```

### Monitor M&A Activity
```python
# M&A related forms
ma_forms = ["8-K", "S-4", "DEFM14A"]
filings = company.get_filings(form=ma_forms)
```

### Find New IPOs
```python
# IPO registrations
ipo_forms = ["S-1", "S-1/A", "F-1"]
filings = get_filings(form=ipo_forms, year=2024)
```

### Hedge Fund Holdings
```python
# 13F filings (institutional managers)
filings = get_filings(form="13F-HR", year=2024, quarter=4)
```
