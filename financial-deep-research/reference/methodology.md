# Financial Deep Research Methodology: 8-Phase Pipeline

## Overview

This document contains the detailed methodology for conducting financial deep research. The 8 phases represent a comprehensive approach to gathering, verifying, and synthesizing financial information from multiple sources with institutional-quality standards.

---

## Phase 1: SCOPE - Financial Research Framing

**Objective:** Define financial research boundaries and success criteria

**Activities:**
1. Decompose the financial question into core components
   - Company/sector identification
   - Time period scope
   - Specific metrics of interest
   - Investment thesis type (growth, value, income, etc.)
2. Identify stakeholder perspectives (investor, analyst, management, regulatory)
3. Define scope boundaries (what's in/out)
   - Geographic scope (US, global, specific regions)
   - Time horizon (near-term, long-term)
   - Analysis type (fundamental, technical, both)
4. Establish success criteria
   - Key questions to answer
   - Required confidence level
   - Specific deliverables
5. List key assumptions to validate

**Financial-Specific Considerations:**
- Jurisdiction for regulatory analysis (SEC for US, etc.)
- Currency for financial metrics
- Fiscal year vs calendar year
- GAAP vs non-GAAP metrics

**Output:** Structured scope document with financial research boundaries

---

## Phase 2: PLAN - Financial Research Strategy

**Objective:** Create an intelligent financial research roadmap

**Activities:**
1. Identify primary and secondary financial sources
   - Tier 1: SEC filings, company IR, regulatory sources
   - Tier 2: Bloomberg, Reuters, S&P, Morningstar
   - Tier 3: Financial news, institutional research
   - Tier 4: General business sources
2. Map knowledge dependencies (what must be understood first)
   - Business model before valuation
   - Historical performance before projections
   - Industry dynamics before competitive positioning
3. Create search query strategy with variants
   - Company-specific searches
   - Industry/sector searches
   - Regulatory/compliance searches
   - Competitive analysis searches
4. Plan triangulation approach for financial data
5. Estimate time/effort per phase
6. Define quality gates

**Financial Search Strategy Template:**
- `[Ticker] SEC 10-K filing 2024` (annual report)
- `[Ticker] SEC 10-Q filing Q3 2024` (quarterly)
- `[Ticker] earnings call transcript Q3 2024`
- `[Company] investor presentation 2024`
- `[Sector] market analysis 2024`
- `[Company] vs [Competitor] comparison`
- `[Company] analyst ratings price target`
- `[Company] risk factors regulatory`

**Output:** Financial research plan with prioritized investigation paths

---

## Phase 3: RETRIEVE - Parallel Financial Information Gathering

**Objective:** Systematically collect financial information using parallel execution for maximum speed

**CRITICAL: Execute ALL searches in parallel using a single message with multiple tool calls**

### Financial Query Decomposition Strategy

Before launching searches, decompose the research question into 5-10 independent search angles:

1. **Company fundamentals** - 10-K/10-Q filings, financial statements
2. **Recent performance** - Earnings, revenue, margins, growth rates
3. **Valuation data** - Multiples, peer comparison, analyst targets
4. **Competitive landscape** - Market share, competitors, moat analysis
5. **Industry dynamics** - Sector trends, TAM, growth drivers
6. **Regulatory environment** - Compliance, pending regulation, risks
7. **Management & governance** - Insider activity, executive track record
8. **Risk factors** - Business risks, financial risks, market risks
9. **Catalysts & events** - Upcoming earnings, product launches, M&A
10. **Bear case** - Short thesis, criticisms, concerns

### Parallel Execution Protocol

**Step 1: Launch ALL financial searches concurrently (single message)**

Choose ONE search approach per research session:

**Using WebSearch (built-in):**
```
[Single message with 8+ parallel tool calls]
- WebSearch(query="AAPL SEC 10-K 2024 annual report")
- WebSearch(query="Apple Q4 2024 earnings revenue margins")
- WebSearch(query="Apple stock valuation P/E ratio analysis 2024")
- WebSearch(query="Apple vs Samsung vs Google competitive analysis")
- WebSearch(query="smartphone market share trends 2024")
- WebSearch(query="Apple regulatory antitrust risk 2024")
- WebSearch(query="Apple analyst ratings price target 2024")
- WebSearch(query="Apple stock bear case risks concerns")
```

**Step 2: Spawn parallel deep-dive agents**

Use Task tool with general-purpose agents (3-5 agents) for:
- SEC filing deep analysis (10-K, 10-Q sections)
- Financial statement analysis (income, balance sheet, cash flow)
- Peer comparison and valuation modeling
- Industry report analysis

**Example parallel agent deployment:**
```
Task(subagent_type="general-purpose", description="SEC 10-K analysis",
     prompt="Analyze Apple's most recent 10-K filing. Extract: business description,
     risk factors, MD&A highlights, segment breakdown, key financial metrics")

Task(subagent_type="general-purpose", description="Financial statement analysis",
     prompt="Analyze Apple's financial statements from recent filings. Calculate:
     revenue growth, margin trends, ROIC, FCF conversion, balance sheet strength")

Task(subagent_type="general-purpose", description="Competitive analysis",
     prompt="Compare Apple's financial metrics and market position vs Samsung,
     Google, Microsoft. Focus on: revenue mix, margins, growth rates, R&D spend")
```

**Step 3: Collect and organize financial results**

As results arrive:
1. Extract key financial metrics with source metadata
2. Track information gaps that emerge
3. Follow promising tangents with targeted searches
4. Maintain source diversity (regulatory, data providers, news)
5. Monitor for quality threshold (see FFS pattern below)

### First Finish Search (FFS) Pattern for Financial Research

**Adaptive completion based on quality threshold:**

**Quality gate:** Proceed to Phase 4 when FIRST threshold reached:
- **Quick mode:** 10+ sources with avg credibility >70/100 OR 2 minutes elapsed
- **Standard mode:** 15+ sources with avg credibility >70/100 OR 5 minutes elapsed
- **Deep mode:** 25+ sources with avg credibility >75/100 OR 10 minutes elapsed
- **UltraDeep mode:** 30+ sources with avg credibility >80/100 OR 15 minutes elapsed

**Continue background searches:**
- If threshold reached early, continue remaining parallel searches in background
- Additional sources used in Phase 5 (SYNTHESIZE) for depth
- Allows fast progression without sacrificing thoroughness

### Financial Source Quality Standards

**Source diversity requirements:**
- Minimum 2 Tier 1 sources (SEC filings, company IR)
- At least 3 different source tiers represented
- Mix of quantitative (filings) and qualitative (analysis) sources
- Recent data (within 6 months for quarterly data)

**Credibility tracking:**
- Score each source 0-100 using financial source_evaluator.py
- Tier 1 sources: 90-100 baseline
- Tier 2 sources: 70-85 baseline
- Tier 3 sources: 60-75 baseline
- Tier 4 sources: 40-60 baseline
- Flag low-credibility sources (<60) for verification
- Prioritize high-credibility sources (>80) for core financial claims

**Output:** Organized financial information repository with source tracking, credibility scores, and coverage map

---

## Phase 4: TRIANGULATE - Financial Cross-Reference Verification

**Objective:** Validate financial information across multiple independent sources

**Activities:**
1. Identify financial claims requiring verification
   - Revenue/earnings figures
   - Margin calculations
   - Growth rates
   - Valuation multiples
   - Market share claims
2. Cross-reference facts across 3+ sources
   - Primary source (SEC filing) vs data providers
   - Multiple analyst estimates
   - News reports vs company statements
3. Flag contradictions or uncertainties
4. Assess source credibility tier
5. Note consensus vs. debate areas
6. Document verification status per claim

**Financial-Specific Verification:**
- Cross-check key metrics against SEC filings
- Verify analyst estimates across multiple providers
- Confirm market data with exchange sources
- Validate regulatory claims with official sources

**Quality Standards:**
- Core financial claims must have 2+ independent sources (one being Tier 1)
- Flag any single-source financial information
- Note data recency (filing date, report date)
- Identify potential biases (sell-side vs buy-side)

**Output:** Verified financial fact base with confidence levels

---

## Phase 4.5: OUTLINE REFINEMENT - Dynamic Evolution (WebWeaver 2025)

**Objective:** Adapt financial research direction based on evidence discovered

**Problem Solved:** Prevents "locked-in" research when evidence points to different conclusions or uncovers more important financial angles than initially planned.

**When to Execute:**
- **Standard/Deep/UltraDeep modes only** (Quick mode skips this)
- After Phase 4 (TRIANGULATE) completes
- Before Phase 5 (SYNTHESIZE)

**Financial-Specific Adaptation Signals:**
- Major risk factor not in original scope
- Valuation discrepancy requiring deeper analysis
- Regulatory issue more significant than expected
- Competitive threat underappreciated
- Financial health concerns emerged
- Management credibility issues surfaced

**Activities:**

1. **Review Initial Scope vs. Actual Findings**
   - Compare Phase 1 scope with Phase 3-4 discoveries
   - Identify unexpected financial patterns
   - Note underexplored angles that emerged as critical

2. **Evaluate Outline Adaptation Need**

   **Signals for adaptation:**
   - Major financial risks not in original outline
   - Valuation thesis challenged by evidence
   - Competitive dynamics more complex than expected
   - Regulatory environment more impactful

3. **Refine Outline (if needed)**

   **Example adaptation:**
   ```
   Original outline:
   1. Company Overview
   2. Financial Analysis
   3. Valuation
   4. Recommendation

   Refined after Phase 4 (debt concerns emerged):
   1. Company Overview
   2. Financial Analysis
   3. **Balance Sheet Deep Dive (NEW - debt concerns)**
   4. **Liquidity Risk Assessment (NEW - material issue)**
   5. Valuation (adjusted for risk)
   6. Recommendation with Risk Caveats
   ```

4. **Targeted Gap Filling (if major gaps found)**
   - Launch 2-3 targeted searches for newly identified angles
   - Quick retrieval only (don't restart full Phase 3)
   - Time-box to 2-5 minutes

**Output:** Refined outline that accurately reflects financial evidence landscape

---

## Phase 5: SYNTHESIZE - Financial Deep Analysis

**Objective:** Connect financial insights and generate investment understanding

**Activities:**
1. Identify patterns across financial sources
   - Revenue trends and drivers
   - Margin trajectory and sustainability
   - Cash flow dynamics
   - Balance sheet evolution
2. Map relationships between financial concepts
   - Revenue growth vs profitability
   - Capex vs FCF generation
   - Leverage vs interest coverage
3. Generate insights beyond source material
   - Investment thesis development
   - Valuation framework
   - Risk/reward assessment
4. Create financial frameworks
   - Bull case / Base case / Bear case
   - Key metrics dashboard
   - Peer comparison matrix
5. Build argument structures
   - Investment thesis support
   - Counter-arguments addressed
6. Develop evidence hierarchies
   - Primary evidence (filings, data)
   - Supporting evidence (analysis, news)

**Financial Synthesis Framework:**
- **Bull Case**: Best-case scenario with supporting evidence
- **Base Case**: Most likely outcome with key assumptions
- **Bear Case**: Downside risks and worst-case scenario
- **Key Metrics**: 5-10 most important financial metrics
- **Catalysts**: Near-term and long-term value drivers
- **Risks**: Ranked by probability and impact

**Output:** Synthesized financial understanding with investment insight generation

---

## Phase 6: CRITIQUE - Financial Quality Assurance

**Objective:** Rigorously evaluate financial research quality

**Activities:**
1. Review for logical consistency
   - Financial calculations check
   - Ratio consistency
   - Growth rate plausibility
2. Check citation completeness
   - Every financial claim cited
   - Source tier documented
3. Identify gaps or weaknesses
   - Missing data points
   - Outdated information
   - Single-source claims
4. Assess balance and objectivity
   - Bull vs bear balance
   - Bias identification
5. Verify claims against sources
   - Spot-check key metrics
   - Confirm SEC filing accuracy
6. Test alternative interpretations
   - Consider counter-thesis
   - Stress-test assumptions

**Financial Red Team Questions:**
- What's the strongest bear case?
- What could make this investment fail?
- What are management's incentives?
- What are we missing?
- What if growth slows?
- What if margins compress?
- What regulatory risks exist?

**Output:** Financial critique report with improvement recommendations

---

## Phase 7: REFINE - Financial Iterative Improvement

**Objective:** Address gaps and strengthen financial analysis

**Activities:**
1. Conduct additional research for financial gaps
2. Strengthen weak investment arguments
3. Add missing financial perspectives
4. Resolve data contradictions
5. Enhance clarity of financial explanation
6. Verify revised financial content

**Financial-Specific Refinement:**
- Update with most recent filings if available
- Strengthen valuation analysis
- Add peer comparison depth
- Expand risk factor coverage
- Include management track record

**Output:** Strengthened financial research with addressed deficiencies

---

## Phase 8: PACKAGE - Financial Report Generation

**Objective:** Deliver professional, institutional-quality financial research

**Activities:**
1. Structure report with financial hierarchy
   - Executive summary with thesis
   - Key metrics dashboard
   - Detailed analysis sections
   - Risk factors
   - Recommendations
2. Write executive summary with clear investment thesis
3. Develop detailed financial sections
4. Create financial visualizations (tables, charts)
5. Compile full bibliography with source tiers
6. Add methodology appendix

**Financial Report Structure:**
1. Executive Summary (thesis, key metrics, recommendation)
2. Company Overview (business model, segments, management)
3. Financial Analysis (income, balance sheet, cash flow)
4. Valuation Analysis (multiples, DCF, peer comparison)
5. Competitive Position (market share, moat, dynamics)
6. Risk Factors (business, financial, regulatory, market)
7. Investment Thesis (bull/base/bear cases)
8. Recommendations (action items, catalysts to watch)
9. Bibliography (tiered, with URLs)
10. Methodology Appendix

**Output:** Complete financial research report ready for institutional use

---

## Advanced Financial Features

### Financial Source Prioritization

Automatic prioritization based on:
- Regulatory filings (highest priority for factual data)
- Data providers (high priority for analytics)
- Financial news (medium priority for context)
- General sources (lowest priority, verification required)

### Parallel Agent Deployment for Financial Research

Use Task tool to spawn sub-agents for:
- SEC filing deep analysis
- Financial statement modeling
- Peer comparison analysis
- Industry research
- Regulatory impact assessment

### Financial Citation Intelligence

Smart citation management:
- Track provenance to original filing
- Link to SEC EDGAR when available
- Assess source tier automatically
- Handle conflicting financial data
- Generate institutional-grade bibliographies

### Valuation Framework Integration

Support for common valuation approaches:
- Comparable company analysis
- Precedent transactions
- DCF framework (when applicable)
- Sum-of-the-parts analysis
