#!/usr/bin/env npx ts-node
/**
 * SEO Analytics Script
 * Analyzes a URL using Google PageSpeed Insights API and generates an HTML report.
 *
 * Usage:
 *   npx ts-node analyze.ts <URL>
 *   npx ts-node analyze.ts https://eng0.ai
 *
 * Output:
 *   - Console summary with all scores
 *   - ./seo-report.html - Interactive HTML report
 */

import * as fs from 'fs';

const url = process.argv[2];
const apiKey = process.argv[3] || process.env.PAGESPEED_API_KEY;

if (!url) {
  console.error('Usage: npx ts-node analyze.ts <URL> [API_KEY]');
  console.error('Example: npx ts-node analyze.ts https://eng0.ai YOUR_API_KEY');
  console.error('');
  console.error('You can also set PAGESPEED_API_KEY environment variable.');
  process.exit(1);
}

interface AuditResult {
  title?: string;
  description?: string;
  score?: number | null;
  displayValue?: string;
  numericValue?: number;
}

interface PageSpeedResult {
  lighthouseResult: {
    categories: {
      performance: { score: number };
      accessibility: { score: number };
      'best-practices': { score: number };
      seo: { score: number };
    };
    audits: {
      [key: string]: AuditResult;
    };
  };
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function analyzeUrl(
  targetUrl: string,
  strategy: 'mobile' | 'desktop',
  retries = 5
): Promise<PageSpeedResult> {
  let apiUrl = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(
    targetUrl
  )}&strategy=${strategy}&category=performance&category=accessibility&category=best-practices&category=seo`;

  if (apiKey) {
    apiUrl += `&key=${apiKey}`;
  }

  console.log(`Analyzing ${strategy}...`);

  for (let attempt = 1; attempt <= retries; attempt++) {
    const response = await fetch(apiUrl);
    if (response.ok) {
      return response.json() as Promise<PageSpeedResult>;
    }
    if (response.status === 429 && attempt < retries) {
      const waitTime = attempt * 15000; // 15s, 30s, 45s, 60s
      console.log(`Rate limited. Waiting ${waitTime / 1000}s before retry (attempt ${attempt}/${retries})...`);
      await delay(waitTime);
      continue;
    }
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }
  throw new Error('Max retries exceeded');
}

function getScoreColor(score: number): string {
  if (score >= 90) return '#0cce6b';
  if (score >= 50) return '#ffa400';
  return '#ff4e42';
}

function getVitalStatus(
  value: number | undefined,
  goodThreshold: number,
  needsWorkThreshold: number
): { class: string; text: string } {
  if (value === undefined) return { class: '', text: 'N/A' };
  if (value <= goodThreshold) return { class: 'good', text: 'Good' };
  if (value <= needsWorkThreshold) return { class: 'needs-improvement', text: 'Needs Work' };
  return { class: 'poor', text: 'Poor' };
}

function generateReport(
  mobile: PageSpeedResult,
  desktop: PageSpeedResult,
  targetUrl: string
): string {
  const m = mobile.lighthouseResult;
  const d = desktop.lighthouseResult;

  const mobileScores = {
    performance: Math.round(m.categories.performance.score * 100),
    accessibility: Math.round(m.categories.accessibility.score * 100),
    bestPractices: Math.round(m.categories['best-practices'].score * 100),
    seo: Math.round(m.categories.seo.score * 100),
  };

  const desktopScores = {
    performance: Math.round(d.categories.performance.score * 100),
    accessibility: Math.round(d.categories.accessibility.score * 100),
    bestPractices: Math.round(d.categories['best-practices'].score * 100),
    seo: Math.round(d.categories.seo.score * 100),
  };

  const webVitals = {
    mobile: {
      lcp: m.audits['largest-contentful-paint'],
      tbt: m.audits['total-blocking-time'],
      cls: m.audits['cumulative-layout-shift'],
      fcp: m.audits['first-contentful-paint'],
      si: m.audits['speed-index'],
      tti: m.audits['interactive'],
    },
    desktop: {
      lcp: d.audits['largest-contentful-paint'],
      tbt: d.audits['total-blocking-time'],
      cls: d.audits['cumulative-layout-shift'],
      fcp: d.audits['first-contentful-paint'],
      si: d.audits['speed-index'],
      tti: d.audits['interactive'],
    },
  };

  // Extract top opportunities
  const opportunities: string[] = [];
  for (const [_key, audit] of Object.entries(m.audits)) {
    if (
      audit.score !== undefined &&
      audit.score !== null &&
      audit.score < 0.9 &&
      audit.title &&
      audit.description
    ) {
      opportunities.push(
        `<li><strong>${audit.title}</strong>: ${audit.description.split('.')[0]}.</li>`
      );
    }
  }

  // Helper for vital status
  const lcpStatus = getVitalStatus(webVitals.mobile.lcp?.numericValue, 2500, 4000);
  const tbtStatus = getVitalStatus(webVitals.mobile.tbt?.numericValue, 200, 600);
  const clsStatus = getVitalStatus(webVitals.mobile.cls?.numericValue, 0.1, 0.25);
  const fcpStatus = getVitalStatus(webVitals.mobile.fcp?.numericValue, 1800, 3000);
  const siStatus = getVitalStatus(webVitals.mobile.si?.numericValue, 3400, 5800);
  const ttiStatus = getVitalStatus(webVitals.mobile.tti?.numericValue, 3800, 7300);

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SEO Report - ${targetUrl}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .url { color: #666; font-size: 0.9rem; margin-bottom: 2rem; word-break: break-all; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }
    .card { background: white; border-radius: 8px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .card h2 { font-size: 1.1rem; margin-bottom: 1rem; color: #444; }
    .scores { display: flex; justify-content: space-around; text-align: center; }
    .score-item { display: flex; flex-direction: column; align-items: center; }
    .score-circle { width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold; color: white; margin-bottom: 0.5rem; }
    .score-label { font-size: 0.75rem; color: #666; }
    .vitals-table { width: 100%; border-collapse: collapse; }
    .vitals-table th, .vitals-table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #eee; }
    .vitals-table th { font-weight: 500; color: #666; font-size: 0.85rem; }
    .good { color: #0cce6b; }
    .needs-improvement { color: #ffa400; }
    .poor { color: #ff4e42; }
    .chart-container { position: relative; height: 300px; }
    .opportunities { list-style: none; }
    .opportunities li { padding: 0.75rem 0; border-bottom: 1px solid #eee; font-size: 0.9rem; }
    .opportunities li:last-child { border-bottom: none; }
    .timestamp { text-align: center; color: #999; font-size: 0.8rem; margin-top: 2rem; }
  </style>
</head>
<body>
  <div class="container">
    <h1>SEO Analysis Report</h1>
    <p class="url">${targetUrl}</p>

    <div class="grid">
      <div class="card">
        <h2>Mobile Scores</h2>
        <div class="scores">
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(mobileScores.performance)}">${mobileScores.performance}</div>
            <span class="score-label">Performance</span>
          </div>
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(mobileScores.accessibility)}">${mobileScores.accessibility}</div>
            <span class="score-label">Accessibility</span>
          </div>
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(mobileScores.bestPractices)}">${mobileScores.bestPractices}</div>
            <span class="score-label">Best Practices</span>
          </div>
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(mobileScores.seo)}">${mobileScores.seo}</div>
            <span class="score-label">SEO</span>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Desktop Scores</h2>
        <div class="scores">
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(desktopScores.performance)}">${desktopScores.performance}</div>
            <span class="score-label">Performance</span>
          </div>
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(desktopScores.accessibility)}">${desktopScores.accessibility}</div>
            <span class="score-label">Accessibility</span>
          </div>
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(desktopScores.bestPractices)}">${desktopScores.bestPractices}</div>
            <span class="score-label">Best Practices</span>
          </div>
          <div class="score-item">
            <div class="score-circle" style="background: ${getScoreColor(desktopScores.seo)}">${desktopScores.seo}</div>
            <span class="score-label">SEO</span>
          </div>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Core Web Vitals - Mobile</h2>
        <table class="vitals-table">
          <tr><th>Metric</th><th>Value</th><th>Status</th></tr>
          <tr>
            <td>Largest Contentful Paint (LCP)</td>
            <td>${webVitals.mobile.lcp?.displayValue || 'N/A'}</td>
            <td class="${lcpStatus.class}">${lcpStatus.text}</td>
          </tr>
          <tr>
            <td>Total Blocking Time (TBT)</td>
            <td>${webVitals.mobile.tbt?.displayValue || 'N/A'}</td>
            <td class="${tbtStatus.class}">${tbtStatus.text}</td>
          </tr>
          <tr>
            <td>Cumulative Layout Shift (CLS)</td>
            <td>${webVitals.mobile.cls?.displayValue || 'N/A'}</td>
            <td class="${clsStatus.class}">${clsStatus.text}</td>
          </tr>
          <tr>
            <td>First Contentful Paint (FCP)</td>
            <td>${webVitals.mobile.fcp?.displayValue || 'N/A'}</td>
            <td class="${fcpStatus.class}">${fcpStatus.text}</td>
          </tr>
          <tr>
            <td>Speed Index</td>
            <td>${webVitals.mobile.si?.displayValue || 'N/A'}</td>
            <td class="${siStatus.class}">${siStatus.text}</td>
          </tr>
          <tr>
            <td>Time to Interactive (TTI)</td>
            <td>${webVitals.mobile.tti?.displayValue || 'N/A'}</td>
            <td class="${ttiStatus.class}">${ttiStatus.text}</td>
          </tr>
        </table>
      </div>

      <div class="card">
        <h2>Score Comparison</h2>
        <div class="chart-container">
          <canvas id="comparisonChart"></canvas>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>Optimization Opportunities</h2>
      <ul class="opportunities">
        ${opportunities.slice(0, 10).join('\n        ') || '<li>No significant issues found. Great job!</li>'}
      </ul>
    </div>

    <p class="timestamp">Generated on ${new Date().toLocaleString()}</p>
  </div>

  <script>
    new Chart(document.getElementById('comparisonChart'), {
      type: 'radar',
      data: {
        labels: ['Performance', 'Accessibility', 'Best Practices', 'SEO'],
        datasets: [
          {
            label: 'Mobile',
            data: [${mobileScores.performance}, ${mobileScores.accessibility}, ${mobileScores.bestPractices}, ${mobileScores.seo}],
            borderColor: '#4285f4',
            backgroundColor: 'rgba(66, 133, 244, 0.2)',
          },
          {
            label: 'Desktop',
            data: [${desktopScores.performance}, ${desktopScores.accessibility}, ${desktopScores.bestPractices}, ${desktopScores.seo}],
            borderColor: '#34a853',
            backgroundColor: 'rgba(52, 168, 83, 0.2)',
          }
        ]
      },
      options: {
        scales: { r: { beginAtZero: true, max: 100 } },
        plugins: { legend: { position: 'bottom' } }
      }
    });
  </script>
</body>
</html>`;
}

async function main() {
  try {
    console.log('Starting SEO analysis for:', url);
    console.log('');

    // Sequential requests to avoid rate limiting
    const mobile = await analyzeUrl(url, 'mobile');
    await delay(2000); // Wait 2s between requests
    const desktop = await analyzeUrl(url, 'desktop');

    const report = generateReport(mobile, desktop, url);

    const outputPath = './seo-report.html';
    fs.writeFileSync(outputPath, report);

    // Print summary
    const m = mobile.lighthouseResult;
    const d = desktop.lighthouseResult;

    console.log('');
    console.log('=== SEO Analysis Complete ===');
    console.log('');
    console.log('Mobile Scores:');
    console.log(`  Performance:    ${Math.round(m.categories.performance.score * 100)}/100`);
    console.log(`  Accessibility:  ${Math.round(m.categories.accessibility.score * 100)}/100`);
    console.log(`  Best Practices: ${Math.round(m.categories['best-practices'].score * 100)}/100`);
    console.log(`  SEO:            ${Math.round(m.categories.seo.score * 100)}/100`);
    console.log('');
    console.log('Desktop Scores:');
    console.log(`  Performance:    ${Math.round(d.categories.performance.score * 100)}/100`);
    console.log(`  Accessibility:  ${Math.round(d.categories.accessibility.score * 100)}/100`);
    console.log(`  Best Practices: ${Math.round(d.categories['best-practices'].score * 100)}/100`);
    console.log(`  SEO:            ${Math.round(d.categories.seo.score * 100)}/100`);
    console.log('');
    console.log('Core Web Vitals (Mobile):');
    console.log(`  LCP: ${m.audits['largest-contentful-paint']?.displayValue || 'N/A'}`);
    console.log(`  TBT: ${m.audits['total-blocking-time']?.displayValue || 'N/A'}`);
    console.log(`  CLS: ${m.audits['cumulative-layout-shift']?.displayValue || 'N/A'}`);
    console.log('');
    console.log(`Report saved to: ${outputPath}`);
    console.log('Open the HTML file in a browser to view the interactive report.');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();
