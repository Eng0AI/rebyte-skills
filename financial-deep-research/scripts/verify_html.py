#!/usr/bin/env python3
"""
HTML Financial Report Verification Script
Validates that HTML reports are properly generated with all sections from MD
"""

import argparse
import re
from pathlib import Path
from typing import List


class FinancialHTMLVerifier:
    """Verify HTML financial research reports"""

    def __init__(self, html_path: Path, md_path: Path):
        self.html_path = html_path
        self.md_path = md_path
        self.errors = []
        self.warnings = []

    def verify(self) -> bool:
        """Run all verification checks"""
        print(f"\n{'='*60}")
        print(f"HTML FINANCIAL REPORT VERIFICATION")
        print(f"{'='*60}\n")

        print(f"HTML File: {self.html_path}")
        print(f"MD File: {self.md_path}\n")

        try:
            html_content = self.html_path.read_text()
            md_content = self.md_path.read_text()
        except Exception as e:
            self.errors.append(f"Failed to read files: {e}")
            return False

        # Run checks
        self._check_sections(html_content, md_content)
        self._check_no_placeholders(html_content)
        self._check_no_emojis(html_content)
        self._check_structure(html_content)
        self._check_financial_elements(html_content)
        self._check_citations(html_content, md_content)
        self._check_bibliography(html_content, md_content)

        self._print_results()

        return len(self.errors) == 0

    def _check_sections(self, html: str, md: str):
        """Verify all markdown sections are present in HTML"""
        md_sections = re.findall(r'^## (.+)$', md, re.MULTILINE)
        html_sections = re.findall(r'<h2 class="section-title">(.+?)</h2>', html)

        if len(md_sections) > len(html_sections) + 1:
            self.errors.append(
                f"Section count mismatch: MD has {len(md_sections)}, HTML has {len(html_sections)}"
            )

    def _check_no_placeholders(self, html: str):
        """Check for unreplaced placeholders"""
        placeholders = [
            '{{TITLE}}', '{{DATE}}', '{{CONTENT}}', '{{BIBLIOGRAPHY}}',
            '{{METRICS_DASHBOARD}}', '{{SOURCE_COUNT}}', '{{INVESTMENT_THESIS}}',
            'TODO', 'TBD', 'PLACEHOLDER', '$X.XB', 'XX.X%'
        ]

        found = [p for p in placeholders if p in html]
        if found:
            self.errors.append(f"Found unreplaced placeholders: {', '.join(found)}")

    def _check_no_emojis(self, html: str):
        """Verify no emojis in HTML"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"
            "\U0001F300-\U0001F5FF"
            "\U0001F680-\U0001F6FF"
            "\U0001F1E0-\U0001F1FF"
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )

        emojis = emoji_pattern.findall(html)
        if emojis:
            self.errors.append(f"Found {len(emojis)} emojis in HTML (should be none)")

    def _check_structure(self, html: str):
        """Verify HTML has proper structure"""
        required = [
            ('<html', 'HTML tag'),
            ('<head', 'head tag'),
            ('<body', 'body tag'),
            ('<title>', 'title tag'),
            ('class="header"', 'header section'),
            ('class="content"', 'content section'),
            ('class="bibliography"', 'bibliography section'),
        ]

        for element, name in required:
            if element not in html:
                self.errors.append(f"Missing {name} in HTML")

    def _check_financial_elements(self, html: str):
        """Check for financial-specific HTML elements"""
        financial_elements = [
            ('class="metrics-dashboard"', 'Metrics dashboard'),
            ('class="data-table"', 'Data tables'),
        ]

        for element, name in financial_elements:
            if element not in html:
                self.warnings.append(f"Missing {name} (recommended for financial reports)")

        # Check for investment thesis
        if 'investment-thesis' not in html and 'Investment Thesis' not in html:
            self.warnings.append("Missing investment thesis section")

    def _check_citations(self, html: str, md: str):
        """Verify citations are present"""
        md_citations = set(re.findall(r'\[(\d+)\]', md))
        html_content = html.split('class="bibliography"')[0] if 'class="bibliography"' in html else html
        html_citations = set(re.findall(r'\[(\d+)\]', html_content))

        if len(md_citations) > 0 and len(html_citations) == 0:
            self.errors.append("No citations found in HTML content")

    def _check_bibliography(self, html: str, md: str):
        """Verify bibliography is present"""
        if '## Bibliography' in md:
            if 'class="bibliography"' not in html:
                self.errors.append("Bibliography section missing from HTML")

    def _print_results(self):
        """Print verification results"""
        print(f"\n{'-'*60}")
        print("VERIFICATION RESULTS")
        print(f"{'-'*60}\n")

        if self.errors:
            print(f"ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
            print()

        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()

        if not self.errors and not self.warnings:
            print("All checks passed! HTML report is valid.\n")

        print(f"{'-'*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Verify HTML financial report')
    parser.add_argument('--html', type=Path, required=True, help='Path to HTML report')
    parser.add_argument('--md', type=Path, required=True, help='Path to markdown report')

    args = parser.parse_args()

    if not args.html.exists():
        print(f"Error: HTML file not found: {args.html}")
        return 1

    if not args.md.exists():
        print(f"Error: Markdown file not found: {args.md}")
        return 1

    verifier = FinancialHTMLVerifier(args.html, args.md)
    success = verifier.verify()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
