#!/usr/bin/env python3
"""
Financial Research Engine
Core orchestration for financial deep research pipeline

Note: This is a placeholder for the research engine. The actual orchestration
is handled by Claude Code when the skill is invoked. This module provides
utility functions that can be called from the command line for testing.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime


def main():
    """Entry point for financial research engine"""
    parser = argparse.ArgumentParser(
        description="Financial Deep Research Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Financial Research Modes:
  quick      - Market snapshot, 2-5 min, 10+ sources
  standard   - Most analysis, 5-10 min, 15-30 sources (default)
  deep       - Investment decisions, 10-20 min, 25-50 sources
  ultradeep  - M&A due diligence, 20-45 min, 30-100+ sources

Examples:
  python research_engine.py --query "Analyze Apple investment thesis" --mode standard
  python research_engine.py --query "NVDA vs AMD competitive analysis" --mode deep
  python research_engine.py --query "Fintech sector due diligence" --mode ultradeep

Note: This engine is typically invoked through Claude Code's skill system.
Direct CLI usage is for testing and debugging.
        """
    )

    parser.add_argument(
        '--query', '-q',
        type=str,
        required=True,
        help='Financial research query'
    )

    parser.add_argument(
        '--mode', '-m',
        type=str,
        choices=['quick', 'standard', 'deep', 'ultradeep'],
        default='standard',
        help='Research mode (default: standard)'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output directory (default: /code/research_output/)'
    )

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"FINANCIAL DEEP RESEARCH ENGINE")
    print(f"{'='*60}\n")

    print(f"Query: {args.query}")
    print(f"Mode: {args.mode}")
    print(f"Output: {args.output or '/code/research_output/'}")
    print()

    # Mode configuration
    mode_config = {
        'quick': {
            'phases': [1, 3, 8],
            'min_sources': 10,
            'target_time': '2-5 min',
            'description': 'Market snapshot'
        },
        'standard': {
            'phases': [1, 2, 3, 4, 4.5, 5, 8],
            'min_sources': 15,
            'target_time': '5-10 min',
            'description': 'Standard analysis'
        },
        'deep': {
            'phases': [1, 2, 3, 4, 4.5, 5, 6, 7, 8],
            'min_sources': 25,
            'target_time': '10-20 min',
            'description': 'Investment decision'
        },
        'ultradeep': {
            'phases': [1, 2, 3, 4, 4.5, 5, 6, 7, 8],
            'min_sources': 30,
            'target_time': '20-45 min',
            'description': 'M&A due diligence'
        }
    }

    config = mode_config[args.mode]

    print(f"Configuration:")
    print(f"  Phases: {config['phases']}")
    print(f"  Min Sources: {config['min_sources']}")
    print(f"  Target Time: {config['target_time']}")
    print(f"  Description: {config['description']}")
    print()

    print("Note: Full research execution requires Claude Code skill invocation.")
    print("This CLI provides configuration preview and testing utilities.")
    print()

    # Generate output directory name
    timestamp = datetime.now().strftime('%Y%m%d')
    topic_slug = args.query[:30].replace(' ', '_').replace('/', '_')
    output_dir = f"/code/{topic_slug}_Financial_Research_{timestamp}/"

    print(f"Recommended output directory: {output_dir}")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
