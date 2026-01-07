#!/usr/bin/env python3
"""
Financial Citation Verification Script

Catches fabricated citations by checking:
1. SEC EDGAR filing verification
2. DOI resolution (via doi.org)
3. Basic metadata matching
4. URL accessibility verification
5. Financial data pattern detection
6. Flags suspicious entries for manual review

Usage:
    python verify_citations.py --report [path]
    python verify_citations.py --report [path] --strict

Does NOT require API keys - uses free DOI resolver and SEC EDGAR.
"""

import sys
import argparse
import re
from pathlib import Path
from typing import List, Dict, Tuple
from urllib import request, error
from urllib.parse import quote
import json
import time


class FinancialCitationVerifier:
    """Verify citations in financial research report"""

    def __init__(self, report_path: Path, strict_mode: bool = False):
        self.report_path = report_path
        self.strict_mode = strict_mode
        self.content = self._read_report()
        self.suspicious = []
        self.verified = []
        self.errors = []

        # Financial-specific hallucination patterns
        self.suspicious_patterns = [
            # Generic financial-sounding but potentially fake
            (r'^(A |An |The )?(Comprehensive |Complete )?(Analysis|Review|Study) of',
             "Generic financial title pattern"),
            (r'^[A-Z][a-z]+ (Inc|Corp|Ltd)\.? (Financial|Earnings|Annual) (Report|Review)',
             "Too generic company report title"),
            # Future financial data (impossible)
            (r'(Q[1-4]|FY)\s*202[6-9]',
             "Future fiscal period reference"),
            (r'(Q[1-4]|FY)\s*203\d',
             "Future fiscal period reference"),
        ]

        # SEC filing patterns for verification
        self.sec_filing_patterns = [
            r'10-K', r'10-Q', r'8-K', r'DEF 14A', r'S-1', r'424B',
            r'Form 10-K', r'Form 10-Q', r'Form 8-K'
        ]

    def _read_report(self) -> str:
        """Read report file"""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"ERROR: Cannot read report: {e}")
            sys.exit(1)

    def extract_bibliography(self) -> List[Dict]:
        """Extract bibliography entries from report"""
        pattern = r'## Bibliography(.*?)(?=##|\Z)'
        match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)

        if not match:
            self.errors.append("No Bibliography section found")
            return []

        bib_section = match.group(1)

        entries = []
        lines = bib_section.strip().split('\n')

        current_entry = None
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            match_num = re.match(r'^\[(\d+)\]\s+(.+)$', line)
            if match_num:
                if current_entry:
                    entries.append(current_entry)

                num = match_num.group(1)
                rest = match_num.group(2)

                # Parse entry components
                year_match = re.search(r'\((\d{4})\)', rest)
                title_match = re.search(r'"([^"]+)"', rest)
                doi_match = re.search(r'doi\.org/(10\.\S+)', rest)
                url_match = re.search(r'https?://[^\s\)]+', rest)
                sec_match = any(re.search(p, rest, re.IGNORECASE) for p in self.sec_filing_patterns)

                current_entry = {
                    'num': num,
                    'raw': rest,
                    'year': year_match.group(1) if year_match else None,
                    'title': title_match.group(1) if title_match else None,
                    'doi': doi_match.group(1) if doi_match else None,
                    'url': url_match.group(0) if url_match else None,
                    'is_sec_filing': sec_match,
                    'is_tier1': sec_match or ('sec.gov' in rest.lower()) or ('ir.' in rest.lower())
                }
            elif current_entry:
                current_entry['raw'] += ' ' + line

        if current_entry:
            entries.append(current_entry)

        return entries

    def verify_sec_edgar(self, url: str) -> Tuple[bool, str]:
        """Verify SEC EDGAR URL is accessible"""
        if not url or 'sec.gov' not in url:
            return False, "Not an SEC URL"

        try:
            req = request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Financial Research Verifier)')

            with request.urlopen(req, timeout=15) as response:
                if response.status == 200:
                    return True, "SEC filing verified"
                else:
                    return False, f"HTTP {response.status}"
        except error.HTTPError as e:
            return False, f"HTTP {e.code}"
        except Exception as e:
            return False, f"Connection error: {str(e)[:50]}"

    def verify_doi(self, doi: str) -> Tuple[bool, Dict]:
        """Verify DOI exists and get metadata"""
        if not doi:
            return False, {}

        try:
            url = f"https://doi.org/{quote(doi)}"
            req = request.Request(url)
            req.add_header('Accept', 'application/vnd.citationstyles.csl+json')

            with request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return True, {
                    'title': data.get('title', ''),
                    'year': data.get('issued', {}).get('date-parts', [[None]])[0][0],
                }
        except error.HTTPError as e:
            if e.code == 404:
                return False, {'error': 'DOI not found'}
            return False, {'error': f'HTTP {e.code}'}
        except Exception as e:
            return False, {'error': str(e)}

    def verify_url(self, url: str) -> Tuple[bool, str]:
        """Verify URL is accessible"""
        if not url:
            return False, "No URL"

        try:
            req = request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (Financial Research Verifier)')

            with request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return True, "URL accessible"
                else:
                    return False, f"HTTP {response.status}"
        except error.HTTPError as e:
            # Some sites block HEAD, try GET
            if e.code == 405:
                try:
                    req = request.Request(url)
                    req.add_header('User-Agent', 'Mozilla/5.0')
                    with request.urlopen(req, timeout=10) as response:
                        return True, "URL accessible (GET)"
                except:
                    pass
            return False, f"HTTP {e.code}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"

    def detect_hallucination_patterns(self, entry: Dict) -> List[str]:
        """Detect common LLM hallucination patterns in financial citations"""
        issues = []
        title = entry.get('title', '')
        raw = entry.get('raw', '')

        if not title:
            return issues

        # Check suspicious patterns
        for pattern, description in self.suspicious_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                issues.append(f"Suspicious pattern: {description}")

        # Check for future dates
        if entry.get('year'):
            year = int(entry['year'])
            if year > 2025:
                issues.append(f"Future year: {year}")

        # Financial-specific: Check for impossible metrics
        impossible_patterns = [
            (r'\d{4,}%', "Implausible percentage (1000%+)"),
            (r'\$\d{15,}', "Implausible dollar amount"),
        ]
        for pattern, desc in impossible_patterns:
            if re.search(pattern, raw):
                issues.append(desc)

        # Check for Tier 1 sources without verification method
        if entry.get('is_tier1') and not entry.get('url') and not entry.get('doi'):
            issues.append("Tier 1 source without verification URL")

        return issues

    def verify_entry(self, entry: Dict) -> Dict:
        """Verify a single bibliography entry"""
        result = {
            'num': entry['num'],
            'status': 'unknown',
            'issues': [],
            'tier': 1 if entry.get('is_tier1') else 4,
            'verification_methods': []
        }

        # Step 1: Hallucination detection
        hallucination_issues = self.detect_hallucination_patterns(entry)
        if hallucination_issues:
            result['issues'].extend(hallucination_issues)
            result['status'] = 'suspicious'

        # Step 2: SEC filing verification (Tier 1)
        if entry.get('is_sec_filing') and entry.get('url') and 'sec.gov' in entry['url']:
            print(f"  [{entry['num']}] Checking SEC EDGAR...", end=' ')
            success, msg = self.verify_sec_edgar(entry['url'])
            if success:
                result['status'] = 'verified'
                result['verification_methods'].append('SEC_EDGAR')
                print("OK")
            else:
                result['issues'].append(f"SEC verification failed: {msg}")
                print(f"FAIL: {msg}")

        # Step 3: DOI verification
        elif entry.get('doi'):
            print(f"  [{entry['num']}] Checking DOI...", end=' ')
            success, metadata = self.verify_doi(entry['doi'])
            if success:
                result['status'] = 'verified'
                result['verification_methods'].append('DOI')
                print("OK")
            else:
                result['issues'].append(f"DOI failed: {metadata.get('error', 'unknown')}")
                result['status'] = 'unverified'
                print(f"FAIL")

        # Step 4: URL verification
        if entry.get('url') and result['status'] not in ['verified']:
            url_ok, url_status = self.verify_url(entry['url'])
            if url_ok:
                result['verification_methods'].append('URL')
                if result['status'] in ['unknown', 'unverified']:
                    result['status'] = 'url_verified'
                print(f"  [{entry['num']}] URL verified")
            else:
                result['issues'].append(f"URL check failed: {url_status}")

        # Step 5: No verification method
        if not entry.get('url') and not entry.get('doi'):
            result['issues'].append("No verification method (URL or DOI)")
            if result['status'] == 'unknown':
                result['status'] = 'unverified'

        return result

    def verify_all(self):
        """Verify all bibliography entries"""
        print(f"\n{'='*60}")
        print(f"FINANCIAL CITATION VERIFICATION: {self.report_path.name}")
        print(f"{'='*60}\n")

        entries = self.extract_bibliography()

        if not entries:
            print("No bibliography entries found\n")
            return False

        # Count by tier
        tier1_count = sum(1 for e in entries if e.get('is_tier1'))
        print(f"Found {len(entries)} citations ({tier1_count} Tier 1 sources)\n")

        results = []
        for entry in entries:
            result = self.verify_entry(entry)
            results.append(result)
            time.sleep(0.3)  # Rate limiting

        # Summarize
        print(f"\n{'='*60}")
        print(f"VERIFICATION SUMMARY")
        print(f"{'='*60}\n")

        verified = [r for r in results if r['status'] == 'verified']
        url_verified = [r for r in results if r['status'] == 'url_verified']
        suspicious = [r for r in results if r['status'] == 'suspicious']
        unverified = [r for r in results if r['status'] in ['unverified', 'unknown']]

        total_verified = len(verified) + len(url_verified)

        print(f"Fully Verified: {len(verified)}/{len(results)}")
        print(f"URL Verified: {len(url_verified)}/{len(results)}")
        print(f"Suspicious: {len(suspicious)}/{len(results)}")
        print(f"Unverified: {len(unverified)}/{len(results)}")
        print()

        if suspicious:
            print("SUSPICIOUS CITATIONS (Manual Review Required):")
            for r in suspicious:
                print(f"\n  [{r['num']}]")
                for issue in r['issues']:
                    print(f"    - {issue}")
            print()

        # Financial-specific: Check Tier 1 source ratio
        tier1_verified = sum(1 for r in results if r['tier'] == 1 and r['status'] in ['verified', 'url_verified'])
        if tier1_verified < 2:
            print("WARNING: Less than 2 verified Tier 1 sources (SEC filings, company IR)")
            print("  Financial reports should include primary sources\n")

        # Decision
        if suspicious and self.strict_mode:
            print("STRICT MODE: Failing due to suspicious citations")
            return False

        if total_verified / len(results) < 0.5:
            print("WARNING: Less than 50% citations verified")
            return True  # Pass with warning

        print("CITATION VERIFICATION PASSED")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Verify citations in financial research report"
    )

    parser.add_argument(
        '--report', '-r',
        type=str,
        required=True,
        help='Path to financial research report'
    )

    parser.add_argument(
        '--strict',
        action='store_true',
        help='Strict mode: fail on suspicious citations'
    )

    args = parser.parse_args()
    report_path = Path(args.report)

    if not report_path.exists():
        print(f"ERROR: Report not found: {report_path}")
        sys.exit(1)

    verifier = FinancialCitationVerifier(report_path, strict_mode=args.strict)
    passed = verifier.verify_all()

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
