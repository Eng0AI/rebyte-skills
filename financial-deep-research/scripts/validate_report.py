#!/usr/bin/env python3
"""
Financial Report Validation Script
Ensures financial research reports meet quality standards before delivery
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


class FinancialReportValidator:
    """Validates financial research report quality"""

    def __init__(self, report_path: Path):
        self.report_path = report_path
        self.content = self._read_report()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _read_report(self) -> str:
        """Read report file"""
        try:
            with open(self.report_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"ERROR: Cannot read report: {e}")
            sys.exit(1)

    def validate(self) -> bool:
        """Run all validation checks"""
        print(f"\n{'='*60}")
        print(f"VALIDATING FINANCIAL REPORT: {self.report_path.name}")
        print(f"{'='*60}\n")

        checks = [
            ("Executive Summary", self._check_executive_summary),
            ("Required Sections", self._check_required_sections),
            ("Financial Sections", self._check_financial_sections),
            ("Citations", self._check_citations),
            ("Bibliography", self._check_bibliography),
            ("Placeholder Text", self._check_placeholders),
            ("Content Truncation", self._check_content_truncation),
            ("Word Count", self._check_word_count),
            ("Source Count", self._check_source_count),
            ("Financial Data", self._check_financial_data),
            ("Broken Links", self._check_broken_references),
        ]

        for check_name, check_func in checks:
            print(f"Checking: {check_name}...", end=" ")
            passed = check_func()
            if passed:
                print("PASS")
            else:
                print("FAIL")

        self._print_summary()

        return len(self.errors) == 0

    def _check_executive_summary(self) -> bool:
        """Check executive summary exists and is under 250 words"""
        pattern = r'## Executive Summary(.*?)(?=##|\Z)'
        match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)

        if not match:
            self.errors.append("Missing 'Executive Summary' section")
            return False

        summary = match.group(1).strip()
        word_count = len(summary.split())

        if word_count > 300:
            self.warnings.append(f"Executive summary too long: {word_count} words (should be <=250)")

        if word_count < 50:
            self.warnings.append(f"Executive summary too short: {word_count} words (should be >=50)")

        # Check for investment thesis
        if 'thesis' not in summary.lower() and 'recommendation' not in summary.lower():
            self.warnings.append("Executive summary missing clear investment thesis/recommendation")

        return True

    def _check_required_sections(self) -> bool:
        """Check all required sections are present"""
        required = [
            "Executive Summary",
            "Overview",  # Company/Topic Overview
            "Financial Analysis",
            "Valuation",
            "Competitive",  # Competitive Position
            "Risk",  # Risk Factors
            "Recommendation",
            "Bibliography",
            "Methodology"
        ]

        missing = []
        for section in required:
            if not re.search(rf'##.*{section}', self.content, re.IGNORECASE):
                missing.append(section)

        if missing:
            self.errors.append(f"Missing required sections: {', '.join(missing)}")
            return False

        return True

    def _check_financial_sections(self) -> bool:
        """Check financial-specific sections"""
        recommended = [
            "Revenue",
            "Margin",
            "Cash Flow",
            "Balance Sheet",
            "Bull Case",
            "Bear Case"
        ]

        missing_recommended = []
        for section in recommended:
            if section.lower() not in self.content.lower():
                missing_recommended.append(section)

        if len(missing_recommended) > 3:
            self.warnings.append(f"Missing recommended financial content: {', '.join(missing_recommended)}")

        return True

    def _check_citations(self) -> bool:
        """Check citation format and presence"""
        citations = re.findall(r'\[(\d+)\]', self.content)

        if not citations:
            self.errors.append("No citations found in report")
            return False

        unique_citations = set(citations)

        if len(unique_citations) < 10:
            self.warnings.append(f"Only {len(unique_citations)} unique sources cited (recommended: >=10)")

        # Check for consecutive citation numbers
        citation_nums = sorted([int(c) for c in unique_citations])
        if citation_nums:
            max_citation = max(citation_nums)
            expected = set(range(1, max_citation + 1))
            missing = expected - set(citation_nums)

            if missing:
                self.warnings.append(f"Non-consecutive citation numbers, missing: {sorted(missing)}")

        return True

    def _check_bibliography(self) -> bool:
        """Check bibliography exists, matches citations, and has no truncation placeholders"""
        pattern = r'## Bibliography(.*?)(?=##|\Z)'
        match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)

        if not match:
            self.errors.append("Missing 'Bibliography' section")
            return False

        bib_section = match.group(1)

        # Check for truncation placeholders
        truncation_patterns = [
            (r'\[\d+-\d+\]', 'Citation range (e.g., [8-75])'),
            (r'Additional.*citations', 'Phrase "Additional citations"'),
            (r'would be included', 'Phrase "would be included"'),
            (r'\[\.\.\.continue', 'Pattern "[...continue"'),
            (r'\[Continue with', 'Pattern "[Continue with"'),
            (r'etc\.(?!\w)', 'Standalone "etc."'),
        ]

        for pattern_re, description in truncation_patterns:
            if re.search(pattern_re, bib_section, re.IGNORECASE):
                self.errors.append(f"CRITICAL: Bibliography contains truncation placeholder: {description}")
                return False

        # Count bibliography entries
        bib_entries = re.findall(r'^\[(\d+)\]', bib_section, re.MULTILINE)

        if not bib_entries:
            self.errors.append("Bibliography has no entries")
            return False

        # Check for tier organization (recommended for financial)
        if 'Tier 1' not in bib_section and 'tier 1' not in bib_section.lower():
            self.warnings.append("Bibliography not organized by source tier (recommended for financial reports)")

        # Find citations in text
        text_citations = set(re.findall(r'\[(\d+)\]', self.content))
        bib_citations = set(bib_entries)

        # Check all citations have bibliography entries
        missing_in_bib = text_citations - bib_citations
        if missing_in_bib:
            self.errors.append(f"Citations missing from bibliography: {sorted(missing_in_bib)}")
            return False

        return True

    def _check_placeholders(self) -> bool:
        """Check for placeholder text that shouldn't be in final report"""
        placeholders = [
            'TBD', 'TODO', 'FIXME', 'XXX',
            '[citation needed]', '[needs citation]',
            '[placeholder]', '[TODO]', '[TBD]',
            '$X.XB', 'XX.X%', '[N]'  # Template placeholders
        ]

        found_placeholders = []
        for placeholder in placeholders:
            if placeholder in self.content:
                found_placeholders.append(placeholder)

        if found_placeholders:
            self.errors.append(f"Found placeholder text: {', '.join(found_placeholders)}")
            return False

        return True

    def _check_content_truncation(self) -> bool:
        """Check for content truncation patterns"""
        truncation_patterns = [
            (r'Content continues', 'Phrase "Content continues"'),
            (r'Due to length', 'Phrase "Due to length"'),
            (r'would continue', 'Phrase "would continue"'),
            (r'\[Sections \d+-\d+', 'Pattern "[Sections X-Y"'),
            (r'Additional sections', 'Phrase "Additional sections"'),
        ]

        for pattern_re, description in truncation_patterns:
            if re.search(pattern_re, self.content, re.IGNORECASE):
                self.errors.append(f"CRITICAL: Content truncation detected: {description}")
                return False

        return True

    def _check_word_count(self) -> bool:
        """Check overall report length"""
        word_count = len(self.content.split())

        if word_count < 1000:
            self.warnings.append(f"Report is very short: {word_count} words (financial reports should be 2000+)")

        print(f"  (Word count: {word_count})")
        return True

    def _check_source_count(self) -> bool:
        """Check minimum source count"""
        pattern = r'## Bibliography(.*?)(?=##|\Z)'
        match = re.search(pattern, self.content, re.DOTALL | re.IGNORECASE)

        if not match:
            return True  # Already caught in bibliography check

        bib_section = match.group(1)
        bib_entries = re.findall(r'^\[(\d+)\]', bib_section, re.MULTILINE)

        source_count = len(set(bib_entries))

        if source_count < 10:
            self.warnings.append(f"Only {source_count} sources (recommended: >=10 for financial reports)")

        # Check for Tier 1 sources (regulatory/primary)
        tier1_indicators = ['sec.gov', 'SEC', '10-K', '10-Q', 'EDGAR', 'investor relations', 'IR']
        tier1_count = sum(1 for indicator in tier1_indicators if indicator in bib_section)

        if tier1_count < 2:
            self.warnings.append("Limited Tier 1 (regulatory/primary) sources - consider adding SEC filings")

        return True

    def _check_financial_data(self) -> bool:
        """Check for presence of key financial data"""
        required_metrics = [
            (r'\$[\d,.]+[BMK]', 'Dollar amounts'),
            (r'\d+\.?\d*%', 'Percentages'),
            (r'FY\d{4}|Q[1-4]\s*\d{4}', 'Fiscal periods'),
        ]

        for pattern, description in required_metrics:
            if not re.search(pattern, self.content):
                self.warnings.append(f"Missing financial data: {description}")

        # Check for financial tables
        if '|' not in self.content:
            self.warnings.append("No data tables found (recommended for financial reports)")

        return True

    def _check_broken_references(self) -> bool:
        """Check for broken internal references"""
        internal_links = re.findall(r'\[.*?\]\((\.\/.*?)\)', self.content)

        broken = []
        for link in internal_links:
            link_path = link.split('#')[0]
            full_path = self.report_path.parent / link_path

            if not full_path.exists():
                broken.append(link)

        if broken:
            self.errors.append(f"Broken internal links: {', '.join(broken)}")
            return False

        return True

    def _print_summary(self):
        """Print validation summary"""
        print(f"\n{'='*60}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*60}\n")

        if self.errors:
            print(f"ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
            print()

        if self.warnings:
            print(f"WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
            print()

        if not self.errors and not self.warnings:
            print("ALL CHECKS PASSED - Report meets financial quality standards!\n")
        elif not self.errors:
            print("VALIDATION PASSED (with warnings)\n")
        else:
            print("VALIDATION FAILED - Please fix errors before delivery\n")


def main():
    parser = argparse.ArgumentParser(
        description="Validate financial research report quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_report.py --report report.md
  python validate_report.py -r ~/research/financial_report_20251104.md
        """
    )

    parser.add_argument(
        '--report', '-r',
        type=str,
        required=True,
        help='Path to financial research report markdown file'
    )

    args = parser.parse_args()

    report_path = Path(args.report)

    if not report_path.exists():
        print(f"ERROR: Report file not found: {report_path}")
        sys.exit(1)

    validator = FinancialReportValidator(report_path)
    passed = validator.validate()

    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
