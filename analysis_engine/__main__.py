"""CLI entry point for analysis engine."""

import argparse
import sys
from .generator import AnalysisGenerator
from .config import AnalysisConfig


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generate job market analysis JSON files'
    )
    
    parser.add_argument(
        '--output',
        default='frontend/api/analysis',
        help='Output directory for JSON files (default: frontend/api/analysis)'
    )
    
    parser.add_argument(
        '--granularity',
        choices=['daily', 'weekly', 'monthly'],
        default='monthly',
        help='Time granularity for temporal analyses (default: monthly)'
    )
    
    parser.add_argument(
        '--min-sample-size',
        type=int,
        default=10,
        help='Minimum sample size for category analysis (default: 10)'
    )
    
    parser.add_argument(
        '--top-n-skills',
        type=int,
        default=20,
        help='Number of top skills to include (default: 20)'
    )
    
    parser.add_argument(
        '--top-n-companies',
        type=int,
        default=50,
        help='Number of top companies to include (default: 50)'
    )
    
    args = parser.parse_args()
    
    # Configure analysis
    config = AnalysisConfig()
    config.GRANULARITY = args.granularity
    config.MIN_SAMPLE_SIZE = args.min_sample_size
    config.TOP_N_SKILLS = args.top_n_skills
    config.TOP_N_COMPANIES = args.top_n_companies
    
    print("=" * 60)
    print("Job Market Analysis Engine")
    print("=" * 60)
    print(f"Output directory: {args.output}")
    print(f"Time granularity: {args.granularity}")
    print(f"Min sample size: {args.min_sample_size}")
    print(f"Top N skills: {args.top_n_skills}")
    print(f"Top N companies: {args.top_n_companies}")
    print("=" * 60)
    print()
    
    # Generate analyses
    generator = AnalysisGenerator(args.output, config)
    exit_code = generator.generate_all()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
