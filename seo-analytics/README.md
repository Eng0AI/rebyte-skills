# SEO Analytics Skill

Generate visual SEO analysis reports using Google PageSpeed Insights API.

## Usage

```bash
# Run the analysis
npx ts-node analyze.ts https://eng0.ai

# Output: ./seo-report.html
```

## Features

- Mobile & Desktop Lighthouse scores
- Core Web Vitals (LCP, TBT, CLS, FCP, SI, TTI)
- Interactive radar chart comparison
- Optimization recommendations
- No API key required (uses free PageSpeed Insights API)

## Report Contents

1. **Score Cards** - Performance, Accessibility, Best Practices, SEO
2. **Core Web Vitals Table** - With Good/Needs Work/Poor indicators
3. **Radar Chart** - Visual comparison of mobile vs desktop
4. **Opportunities** - Top 10 optimization suggestions

## Score Thresholds

| Score | Rating |
|-------|--------|
| 90-100 | Good (green) |
| 50-89 | Needs Improvement (orange) |
| 0-49 | Poor (red) |

## Core Web Vitals Thresholds

| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| LCP | < 2.5s | 2.5-4s | > 4s |
| TBT | < 200ms | 200-600ms | > 600ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |
