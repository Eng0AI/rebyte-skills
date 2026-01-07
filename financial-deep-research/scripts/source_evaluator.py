#!/usr/bin/env python3
"""
Financial Source Credibility Evaluator
Assesses source quality, credibility, and potential biases for financial research
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from urllib.parse import urlparse
from datetime import datetime, timedelta
import re


@dataclass
class CredibilityScore:
    """Represents financial source credibility assessment"""
    overall_score: float  # 0-100
    domain_authority: float  # 0-100
    recency: float  # 0-100
    expertise: float  # 0-100
    bias_score: float  # 0-100 (higher = more neutral)
    tier: int  # 1-4 (1 = highest credibility)
    factors: Dict[str, str]
    recommendation: str  # "high_trust", "moderate_trust", "low_trust", "verify"


class FinancialSourceEvaluator:
    """Evaluates financial source credibility and quality with tiered system"""

    # Tier 1: Primary/Regulatory Sources (Highest Credibility)
    TIER_1_DOMAINS = {
        # SEC & Regulatory
        'sec.gov', 'edgar.sec.gov', 'investor.gov',
        'federalreserve.gov', 'treasury.gov', 'fdic.gov',
        'occ.gov', 'finra.org', 'cftc.gov', 'bis.org',

        # Company IR (pattern-based, checked separately)
        # ir.*, investor.*, investors.*

        # Stock Exchanges
        'nyse.com', 'nasdaq.com', 'ice.com', 'cmegroup.com',

        # International Regulators
        'fca.org.uk', 'esma.europa.eu', 'bafin.de',
    }

    # Tier 2: Financial Data Providers (High Credibility)
    TIER_2_DOMAINS = {
        # Major Data Providers
        'bloomberg.com', 'reuters.com', 'refinitiv.com',
        'spglobal.com', 'capitaliq.com', 'moodys.com',
        'fitchratings.com', 'factset.com', 'morningstar.com',
        'pitchbook.com', 'preqin.com', 'dealogic.com',

        # Research Providers
        'mckinsey.com', 'bcg.com', 'bain.com', 'deloitte.com',
        'pwc.com', 'ey.com', 'kpmg.com',
    }

    # Tier 3: Financial News & Research (Moderate-High Credibility)
    TIER_3_DOMAINS = {
        # Established Financial News
        'wsj.com', 'ft.com', 'barrons.com', 'economist.com',
        'marketwatch.com', 'investopedia.com', 'thestreet.com',

        # Business News
        'cnbc.com', 'fortune.com', 'businessinsider.com',
        'forbes.com', 'bloomberg.com',  # News articles

        # Industry Publications
        'americanbanker.com', 'institutionalinvestor.com',
        'privateequityinternational.com', 'pensions-investments.com',
    }

    # Tier 4: General Business Sources (Moderate Credibility)
    TIER_4_DOMAINS = {
        # General Finance
        'finance.yahoo.com', 'google.com/finance',
        'seekingalpha.com', 'fool.com', 'zacks.com',
        'tipranks.com', 'gurufocus.com',

        # General News
        'nytimes.com', 'washingtonpost.com', 'bbc.com',
        'cnn.com', 'theguardian.com',

        # Tech/Business Blogs
        'medium.com', 'substack.com', 'linkedin.com',
    }

    # Low credibility indicators
    LOW_CREDIBILITY_INDICATORS = [
        'blogspot.com', 'wordpress.com', 'wix.com',
        'reddit.com', 'twitter.com', 'facebook.com',
        'stocktwits.com', 'wallstreetbets',
    ]

    def __init__(self):
        pass

    def evaluate_source(
        self,
        url: str,
        title: str,
        content: Optional[str] = None,
        publication_date: Optional[str] = None,
        author: Optional[str] = None
    ) -> CredibilityScore:
        """Evaluate financial source credibility"""

        domain = self._extract_domain(url)

        # Determine tier first
        tier = self._determine_tier(domain, url)

        # Calculate component scores
        domain_score = self._evaluate_domain_authority(domain, tier)
        recency_score = self._evaluate_recency(publication_date)
        expertise_score = self._evaluate_expertise(domain, title, author, tier)
        bias_score = self._evaluate_bias(domain, title, content, tier)

        # Calculate overall score (weighted average)
        overall = (
            domain_score * 0.40 +  # Higher weight for domain in financial
            recency_score * 0.20 +
            expertise_score * 0.25 +
            bias_score * 0.15
        )

        # Determine factors
        factors = self._identify_factors(
            domain, tier, domain_score, recency_score, expertise_score, bias_score
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(overall, tier)

        return CredibilityScore(
            overall_score=round(overall, 2),
            domain_authority=round(domain_score, 2),
            recency=round(recency_score, 2),
            expertise=round(expertise_score, 2),
            bias_score=round(bias_score, 2),
            tier=tier,
            factors=factors,
            recommendation=recommendation
        )

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www prefix
        domain = domain.replace('www.', '')
        return domain

    def _determine_tier(self, domain: str, url: str) -> int:
        """Determine source tier (1-4)"""

        # Check Tier 1
        if domain in self.TIER_1_DOMAINS:
            return 1
        # Check for company IR sites (Tier 1)
        if any(pattern in domain for pattern in ['ir.', 'investor.', 'investors.']):
            return 1
        # SEC EDGAR links
        if 'sec.gov' in url:
            return 1

        # Check Tier 2
        if domain in self.TIER_2_DOMAINS:
            return 2

        # Check Tier 3
        if domain in self.TIER_3_DOMAINS:
            return 3

        # Check Tier 4
        if domain in self.TIER_4_DOMAINS:
            return 4

        # Check low credibility
        if any(indicator in domain for indicator in self.LOW_CREDIBILITY_INDICATORS):
            return 4  # Lowest tier

        # Unknown domain - default to tier 4
        return 4

    def _evaluate_domain_authority(self, domain: str, tier: int) -> float:
        """Evaluate domain authority based on tier (0-100)"""
        tier_scores = {
            1: 95.0,  # Regulatory/Primary
            2: 82.0,  # Data Providers
            3: 68.0,  # Financial News
            4: 50.0,  # General Business
        }

        base_score = tier_scores.get(tier, 50.0)

        # Bonus for specific high-authority domains
        if 'sec.gov' in domain:
            base_score = 100.0
        elif 'federalreserve.gov' in domain:
            base_score = 98.0
        elif domain in ['bloomberg.com', 'reuters.com']:
            base_score = 88.0

        # Penalty for low credibility indicators
        if any(indicator in domain for indicator in self.LOW_CREDIBILITY_INDICATORS):
            base_score = min(base_score, 35.0)

        return base_score

    def _evaluate_recency(self, publication_date: Optional[str]) -> float:
        """Evaluate information recency (0-100)"""
        if not publication_date:
            return 50.0  # Unknown date

        try:
            pub_date = datetime.fromisoformat(publication_date.replace('Z', '+00:00'))
            age = datetime.now() - pub_date

            # Financial data has stricter recency requirements
            if age < timedelta(days=30):  # < 1 month
                return 100.0
            elif age < timedelta(days=90):  # < 3 months
                return 90.0
            elif age < timedelta(days=180):  # < 6 months
                return 75.0
            elif age < timedelta(days=365):  # < 1 year
                return 60.0
            elif age < timedelta(days=730):  # < 2 years
                return 45.0
            else:
                return 30.0

        except Exception:
            return 50.0

    def _evaluate_expertise(
        self,
        domain: str,
        title: str,
        author: Optional[str],
        tier: int
    ) -> float:
        """Evaluate source expertise (0-100)"""
        base_score = 50.0

        # Tier-based expertise
        tier_expertise = {1: 40, 2: 30, 3: 20, 4: 10}
        base_score += tier_expertise.get(tier, 0)

        # SEC filings are authoritative
        if 'sec.gov' in domain or '10-K' in title or '10-Q' in title:
            base_score += 20

        # Earnings/financial content
        if any(term in title.lower() for term in ['earnings', 'quarterly', 'annual report', 'financial results']):
            base_score += 10

        # Analyst/research content
        if any(term in title.lower() for term in ['analysis', 'research', 'rating', 'estimate']):
            base_score += 5

        # Author credentials
        if author:
            if any(title in author.lower() for title in ['cfa', 'cpa', 'phd', 'analyst', 'economist']):
                base_score += 10

        return min(base_score, 100.0)

    def _evaluate_bias(
        self,
        domain: str,
        title: str,
        content: Optional[str],
        tier: int
    ) -> float:
        """Evaluate potential bias (0-100, higher = more neutral)"""
        base_score = 70.0

        # Tier-based bias (regulatory sources are most neutral)
        tier_bias = {1: 20, 2: 10, 3: 0, 4: -10}
        base_score += tier_bias.get(tier, 0)

        # Check for sensationalism in title
        sensational_indicators = [
            '!', 'shocking', 'crash', 'explode', 'moon', 'rocket',
            'guaranteed', 'secret', 'you won\'t believe', 'millionaire'
        ]
        title_lower = title.lower()
        if any(indicator in title_lower for indicator in sensational_indicators):
            base_score -= 25

        # Promotional content indicators
        promotional = ['buy now', 'limited time', 'act fast', 'don\'t miss']
        if any(promo in title_lower for promo in promotional):
            base_score -= 30

        # Seeking Alpha, retail sources may have bias
        if 'seekingalpha' in domain or 'fool.com' in domain:
            base_score -= 10

        # Check for balance in content
        if content:
            balanced_indicators = ['however', 'risk', 'downside', 'bear case', 'concerns']
            if any(indicator in content.lower() for indicator in balanced_indicators):
                base_score += 10

        return min(max(base_score, 0), 100.0)

    def _identify_factors(
        self,
        domain: str,
        tier: int,
        domain_score: float,
        recency_score: float,
        expertise_score: float,
        bias_score: float
    ) -> Dict[str, str]:
        """Identify key credibility factors"""
        factors = {}

        # Tier factor
        tier_names = {
            1: "Tier 1: Primary/Regulatory source",
            2: "Tier 2: Financial data provider",
            3: "Tier 3: Financial news/research",
            4: "Tier 4: General business source"
        }
        factors['tier'] = tier_names.get(tier, "Unknown tier")

        if domain_score >= 90:
            factors['domain'] = "Highest authority financial source"
        elif domain_score >= 75:
            factors['domain'] = "High authority financial source"
        elif domain_score <= 45:
            factors['domain'] = "Low authority - verify with primary sources"

        if recency_score >= 90:
            factors['recency'] = "Very recent financial data"
        elif recency_score <= 50:
            factors['recency'] = "Dated information - verify currency"

        if expertise_score >= 80:
            factors['expertise'] = "Expert financial source"
        elif expertise_score <= 50:
            factors['expertise'] = "Limited financial expertise"

        if bias_score >= 80:
            factors['bias'] = "Objective/neutral perspective"
        elif bias_score <= 50:
            factors['bias'] = "Potential bias detected"

        return factors

    def _generate_recommendation(self, overall_score: float, tier: int) -> str:
        """Generate trust recommendation"""
        # Tier 1 sources get higher trust
        if tier == 1 and overall_score >= 70:
            return "high_trust"
        elif tier == 1:
            return "moderate_trust"

        # Other tiers
        if overall_score >= 80:
            return "high_trust"
        elif overall_score >= 65:
            return "moderate_trust"
        elif overall_score >= 50:
            return "low_trust"
        else:
            return "verify"


# Example usage
if __name__ == '__main__':
    evaluator = FinancialSourceEvaluator()

    # Test sources
    test_sources = [
        {
            'url': 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000320193',
            'title': 'Apple Inc. 10-K Annual Report 2024',
            'publication_date': '2024-11-01'
        },
        {
            'url': 'https://www.bloomberg.com/news/articles/2024-10-30/apple-earnings',
            'title': 'Apple Reports Record Q4 Revenue',
            'publication_date': '2024-10-30'
        },
        {
            'url': 'https://seekingalpha.com/article/apple-buy-now',
            'title': 'Apple: BUY NOW Before It Explodes!',
            'publication_date': '2024-10-15'
        },
        {
            'url': 'https://ir.apple.com/investor-relations',
            'title': 'Apple Investor Relations - Q4 2024 Earnings Call',
            'publication_date': '2024-10-31'
        }
    ]

    for source in test_sources:
        score = evaluator.evaluate_source(**source)
        print(f"\nSource: {source['title'][:50]}...")
        print(f"URL: {source['url'][:60]}...")
        print(f"Tier: {score.tier}")
        print(f"Overall Score: {score.overall_score}/100")
        print(f"Recommendation: {score.recommendation}")
        print(f"Factors: {score.factors}")
