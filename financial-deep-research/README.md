# Financial Deep Research Skill for Claude Code

A comprehensive financial research engine that brings institutional-quality financial analysis capabilities to Claude Code terminal.

## Overview

This skill is specialized for financial services research, building on the deep-research skill with:
- **Financial data source prioritization**: SEC filings, Bloomberg, Reuters, S&P, Morningstar
- **Regulatory compliance awareness**: SEC, FINRA, Federal Reserve, OCC sources
- **Financial credibility scoring**: Tiered source evaluation for financial data
- **Investment-grade output**: Professional reports suitable for institutional use

## Features

### Core Research Pipeline
- **8.5-Phase Financial Pipeline**: Scope > Plan > Retrieve (Parallel) > Triangulate > Outline Refinement > Synthesize > Critique > Refine > Package
- **Multiple Research Modes**: Quick, Standard, Deep, and UltraDeep
- **Financial-Specific Verification**: SEC filing verification, financial data cross-checking

### Financial Data Sources (Priority Order)

**Tier 1 - Primary/Regulatory (Highest Credibility):**
- SEC EDGAR (10-K, 10-Q, 8-K, proxy statements)
- Federal Reserve (FRED data, monetary policy)
- Company IR (investor relations, earnings calls)
- Exchange filings (NYSE, NASDAQ disclosures)

**Tier 2 - Financial Data Providers:**
- Bloomberg, Reuters, S&P Global
- Moody's, Fitch (credit ratings)
- FactSet, Morningstar, PitchBook

**Tier 3 - Financial News & Research:**
- Wall Street Journal, Financial Times, Barron's
- Institutional research (Goldman, Morgan Stanley)

**Tier 4 - General Business Sources:**
- CNBC, Yahoo Finance (verify with primary sources)
- Seeking Alpha (user-generated, verify claims)

### 2025 Enhancements
- **Auto-Continuation System**: TRUE UNLIMITED length via recursive agent spawning
- **Progressive File Assembly**: Section-by-section generation with quality safeguards
- **Parallel Search Execution**: 5-10 concurrent searches + parallel agents
- **Financial Citation Validation**: SEC filing verification, data accuracy checks
- **McKinsey-Style HTML Reports**: Professional financial dashboards

## Installation

The skill should be installed in `~/.claude/skills/financial-deep-research/`

No additional dependencies required for basic usage.

## Usage

### In Claude Code

Simply invoke the skill:

```
Use financial deep research to analyze Apple's investment thesis
```

Or specify a mode:

```
Use financial deep research in ultradeep mode for M&A due diligence on Nvidia
```

### Example Queries

**Company Analysis:**
```
Use financial deep research to evaluate Tesla's financial health and valuation
```

**Sector Analysis:**
```
Use financial deep research to analyze the fintech sector landscape 2024-2025
```

**Competitive Analysis:**
```
Use financial deep research to compare cloud providers: AWS vs Azure vs GCP
```

**Due Diligence:**
```
Use financial deep research in deep mode for due diligence on Stripe pre-IPO
```

**Earnings Analysis:**
```
Use financial deep research to analyze Microsoft's Q3 2024 earnings and outlook
```

## Research Modes

| Mode | Phases | Duration | Best For |
|------|--------|----------|----------|
| **Quick** | 3 phases | 2-5 min | Market snapshot, earnings preview |
| **Standard** | 6 phases | 5-10 min | Most financial analysis [DEFAULT] |
| **Deep** | 8 phases | 10-20 min | Investment decisions, detailed analysis |
| **UltraDeep** | 8+ phases | 20-45 min | M&A due diligence, comprehensive reports |

## Output

Financial research reports are saved to organized folders in `/code/[Topic]_Financial_Research_[Date]/`

Each report includes:
- Executive Summary with Investment Thesis
- Company/Topic Overview
- Financial Analysis (revenue, margins, cash flow)
- Valuation Analysis (multiples, peer comparison)
- Competitive Position
- Risk Factors
- Investment Thesis / Recommendations
- Full Bibliography
- Methodology Appendix

### Report Formats

1. **Markdown** - Primary source with full analysis
2. **HTML** - McKinsey-style with financial metrics dashboard
3. **PDF** - Professional print format

## Quality Standards

Every financial research output:
- 10+ sources with tier breakdown
- Citations for all financial claims
- Cross-verified data (3+ sources for key metrics)
- SEC filing references when applicable
- Executive summary <250 words with clear thesis
- Risk factors section
- Full bibliography with source URLs

## Financial Source Credibility Scoring

Sources are scored 0-100 based on:
- **Domain authority** (regulatory > data providers > news)
- **Recency** (recent filings > historical data)
- **Expertise** (institutional research > retail analysis)
- **Bias potential** (SEC filings > analyst opinions)

Minimum average credibility score: 70/100 (higher than general research)

## Use Cases

### Investment Analysis
- Buy/sell/hold thesis development
- Valuation analysis and peer comparison
- Earnings analysis and guidance assessment

### Due Diligence
- Pre-acquisition research
- IPO analysis
- Private company assessment

### Sector Research
- Industry landscape mapping
- Competitive dynamics analysis
- Regulatory environment assessment

### Risk Assessment
- Financial health evaluation
- Regulatory risk analysis
- Market risk assessment

## Architecture

```
financial-deep-research/
|-- SKILL.md                         # Main skill definition
|-- README.md                        # This file
|-- reference/
|   +-- methodology.md               # 8-phase financial methodology
|-- templates/
|   |-- report_template.md           # Financial report structure
|   +-- mckinsey_report_template.html # HTML template with financial dashboard
|-- scripts/
|   |-- research_engine.py           # Core orchestration
|   |-- validate_report.py           # Financial report validation
|   |-- citation_manager.py          # Citation tracking
|   |-- source_evaluator.py          # Financial source credibility
|   +-- verify_citations.py          # SEC filing verification
+-- tests/
    +-- fixtures/                    # Test reports
```

## Comparison with Base Deep Research

| Feature | Deep Research | Financial Deep Research |
|---------|---------------|------------------------|
| Source priority | General web | Financial data providers |
| Credibility threshold | 60/100 | 70/100 |
| SEC filing verification | No | Yes |
| Financial metrics dashboard | No | Yes |
| Risk factors section | Optional | Required |
| Valuation analysis | Generic | Financial-specific |
| Regulatory awareness | Basic | Comprehensive |

## Tips for Best Results

1. **Be Specific**: Include ticker symbols, time periods, specific metrics
2. **Set Context**: Specify if for investment decision, due diligence, or research
3. **Choose Appropriate Mode**: Quick for snapshots, Deep for decisions
4. **Request Specific Analysis**: Valuation focus, risk focus, competitive focus
5. **Leverage Citations**: Drill into SEC filings and primary sources

## Limitations

- Not real-time trading advice (data may be delayed)
- Not personalized financial advice (consult professionals)
- Not tax or legal advice (consult professionals)
- Private company data may be limited
- International markets may have fewer sources

## Version

1.0 (2025-01-06) - Initial release based on deep-research v2.2

## License

User skill - modify as needed for your workflow
