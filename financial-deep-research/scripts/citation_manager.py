#!/usr/bin/env python3
"""
Financial Citation Management System
Tracks sources, generates citations, and maintains bibliography with tier tracking
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse
import hashlib


@dataclass
class FinancialCitation:
    """Represents a single financial citation"""
    id: str
    title: str
    url: str
    tier: int  # 1-4 (1 = highest credibility)
    authors: Optional[List[str]] = None
    publication_date: Optional[str] = None
    retrieved_date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    source_type: str = "web"  # sec_filing, data_provider, financial_news, general
    filing_type: Optional[str] = None  # 10-K, 10-Q, 8-K, etc.
    ticker: Optional[str] = None
    doi: Optional[str] = None
    citation_count: int = 0

    def to_markdown(self, index: int) -> str:
        """Generate markdown format citation"""
        tier_label = f"[Tier {self.tier}]" if self.tier else ""
        filing = f" ({self.filing_type})" if self.filing_type else ""
        ticker = f" [{self.ticker}]" if self.ticker else ""

        return f"[{index}]{ticker}{filing} [{self.title}]({self.url}) {tier_label} (Retrieved: {self.retrieved_date})"

    def to_inline(self, index: int) -> str:
        """Generate inline citation [index]"""
        return f"[{index}]"

    def to_bibliography_entry(self, index: int) -> str:
        """Generate full bibliography entry"""
        author_str = ""
        if self.authors:
            if len(self.authors) == 1:
                author_str = f"{self.authors[0]}."
            elif len(self.authors) == 2:
                author_str = f"{self.authors[0]} & {self.authors[1]}."
            else:
                author_str = f"{self.authors[0]} et al."

        date_str = f"({self.publication_date})" if self.publication_date else "(n.d.)"
        filing = f" {self.filing_type}." if self.filing_type else ""

        return f"[{index}] {author_str} {date_str}.{filing} \"{self.title}\". {self.url} (Retrieved: {self.retrieved_date})"


class FinancialCitationManager:
    """Manages financial citations and bibliography with tier organization"""

    # Domain to tier mapping
    TIER_MAPPING = {
        # Tier 1: Regulatory/Primary
        'sec.gov': 1, 'edgar.sec.gov': 1, 'federalreserve.gov': 1,
        'treasury.gov': 1, 'fdic.gov': 1, 'finra.org': 1,

        # Tier 2: Data Providers
        'bloomberg.com': 2, 'reuters.com': 2, 'spglobal.com': 2,
        'moodys.com': 2, 'fitchratings.com': 2, 'factset.com': 2,
        'morningstar.com': 2, 'pitchbook.com': 2,

        # Tier 3: Financial News
        'wsj.com': 3, 'ft.com': 3, 'barrons.com': 3,
        'cnbc.com': 3, 'marketwatch.com': 3,

        # Tier 4: General
        'seekingalpha.com': 4, 'finance.yahoo.com': 4,
    }

    def __init__(self):
        self.citations: Dict[str, FinancialCitation] = {}
        self.citation_order: List[str] = []

    def add_source(
        self,
        url: str,
        title: str,
        authors: Optional[List[str]] = None,
        publication_date: Optional[str] = None,
        source_type: str = "web",
        filing_type: Optional[str] = None,
        ticker: Optional[str] = None,
        doi: Optional[str] = None,
        tier: Optional[int] = None
    ) -> str:
        """Add a financial source and return its citation ID"""
        citation_id = hashlib.md5(url.encode()).hexdigest()[:8]

        if citation_id not in self.citations:
            # Auto-detect tier if not provided
            if tier is None:
                tier = self._detect_tier(url, source_type, filing_type)

            citation = FinancialCitation(
                id=citation_id,
                title=title,
                url=url,
                tier=tier,
                authors=authors,
                publication_date=publication_date,
                source_type=source_type,
                filing_type=filing_type,
                ticker=ticker,
                doi=doi
            )
            self.citations[citation_id] = citation
            self.citation_order.append(citation_id)

        self.citations[citation_id].citation_count += 1
        return citation_id

    def _detect_tier(self, url: str, source_type: str, filing_type: Optional[str]) -> int:
        """Auto-detect source tier based on URL and type"""
        # SEC filings are always Tier 1
        if filing_type or 'sec.gov' in url.lower():
            return 1

        # Company IR sites are Tier 1
        if any(pattern in url.lower() for pattern in ['ir.', 'investor.', 'investors.']):
            return 1

        # Check domain mapping
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')

        for domain_pattern, tier in self.TIER_MAPPING.items():
            if domain_pattern in domain:
                return tier

        # Default to Tier 4
        return 4

    def get_citation_number(self, citation_id: str) -> Optional[int]:
        """Get the citation number for a given ID"""
        try:
            return self.citation_order.index(citation_id) + 1
        except ValueError:
            return None

    def get_inline_citation(self, citation_id: str) -> str:
        """Get inline citation marker [n]"""
        num = self.get_citation_number(citation_id)
        return f"[{num}]" if num else "[?]"

    def generate_bibliography(self, organize_by_tier: bool = True) -> str:
        """Generate full bibliography, optionally organized by tier"""
        if not organize_by_tier:
            lines = ["## Bibliography\n"]
            for i, citation_id in enumerate(self.citation_order, 1):
                citation = self.citations[citation_id]
                lines.append(citation.to_bibliography_entry(i))
            return "\n\n".join(lines)

        # Organize by tier
        lines = ["## Bibliography\n"]

        tier_names = {
            1: "### Tier 1 Sources (Regulatory/Primary)",
            2: "### Tier 2 Sources (Data Providers)",
            3: "### Tier 3 Sources (Financial News/Research)",
            4: "### Tier 4 Sources (General Business)"
        }

        # Group by tier
        tier_citations = {1: [], 2: [], 3: [], 4: []}
        for i, citation_id in enumerate(self.citation_order, 1):
            citation = self.citations[citation_id]
            tier_citations[citation.tier].append((i, citation))

        # Generate by tier
        for tier in [1, 2, 3, 4]:
            if tier_citations[tier]:
                lines.append(f"\n{tier_names[tier]}\n")
                for i, citation in tier_citations[tier]:
                    lines.append(citation.to_bibliography_entry(i))

        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, any]:
        """Get citation statistics"""
        tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for citation in self.citations.values():
            tier_counts[citation.tier] += 1

        return {
            'total_sources': len(self.citations),
            'total_citations': sum(c.citation_count for c in self.citations.values()),
            'tier_breakdown': tier_counts,
            'tier1_percentage': (tier_counts[1] / len(self.citations) * 100) if self.citations else 0,
            'filing_types': self._count_filing_types(),
            'most_cited': self._get_most_cited(5)
        }

    def _count_filing_types(self) -> Dict[str, int]:
        """Count SEC filing types"""
        counts = {}
        for citation in self.citations.values():
            if citation.filing_type:
                counts[citation.filing_type] = counts.get(citation.filing_type, 0) + 1
        return counts

    def _get_most_cited(self, n: int = 5) -> List[tuple]:
        """Get most cited sources"""
        sorted_citations = sorted(
            self.citations.items(),
            key=lambda x: x[1].citation_count,
            reverse=True
        )
        return [(self.get_citation_number(cid), c.title, c.citation_count)
                for cid, c in sorted_citations[:n]]


# Example usage
if __name__ == '__main__':
    manager = FinancialCitationManager()

    # Add SEC filing
    id1 = manager.add_source(
        url="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193",
        title="Apple Inc. Form 10-K Annual Report",
        publication_date="2024",
        source_type="sec_filing",
        filing_type="10-K",
        ticker="AAPL"
    )

    # Add data provider
    id2 = manager.add_source(
        url="https://www.bloomberg.com/quote/AAPL:US",
        title="Apple Inc Stock Price",
        source_type="data_provider"
    )

    # Add financial news
    id3 = manager.add_source(
        url="https://www.wsj.com/articles/apple-earnings-2024",
        title="Apple Reports Q4 Earnings",
        publication_date="2024-10-31",
        source_type="financial_news"
    )

    print(f"Citation 1: {manager.get_inline_citation(id1)}")
    print(f"Citation 2: {manager.get_inline_citation(id2)}")
    print(f"\nBibliography:\n{manager.generate_bibliography()}")
    print(f"\nStatistics:\n{manager.get_statistics()}")
