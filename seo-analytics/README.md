# SEO Analytics Skill

Generate visual SEO analysis reports using Google PageSpeed Insights API.

## Usage

```bash
# Run the analysis with API key
npx ts-node analyze.ts https://eng0.ai YOUR_API_KEY

# Or with environment variable
PAGESPEED_API_KEY=your_key npx ts-node analyze.ts https://eng0.ai

# Output: ./seo-report.html
```

## API Key Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable **PageSpeed Insights API** in APIs & Services > Library
4. Create an API key in APIs & Services > Credentials

## Features

- Mobile & Desktop Lighthouse scores
- Core Web Vitals (LCP, TBT, CLS, FCP, SI, TTI)
- Interactive radar chart comparison
- Optimization recommendations
- API key recommended for reliable access

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
