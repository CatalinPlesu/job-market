#!/usr/bin/env python3
"""
Example script demonstrating how to use the analysis engine.

This script shows how to:
1. Run the analysis engine programmatically
2. Generate analyses with custom configuration
3. Access individual analysis results
"""

from analysis_engine.generator import AnalysisGenerator
from analysis_engine.config import AnalysisConfig
from pathlib import Path
import json


def main():
    """Run analysis engine example."""
    
    print("=" * 60)
    print("Analysis Engine Example")
    print("=" * 60)
    print()
    
    # Configure analysis settings
    config = AnalysisConfig()
    config.GRANULARITY = 'monthly'
    config.MIN_SAMPLE_SIZE = 10
    config.TOP_N_SKILLS = 20
    config.TOP_N_COMPANIES = 50
    
    # Set output directory
    output_dir = "pages/api/analysis"
    
    print(f"Configuration:")
    print(f"  - Time granularity: {config.GRANULARITY}")
    print(f"  - Min sample size: {config.MIN_SAMPLE_SIZE}")
    print(f"  - Top N skills: {config.TOP_N_SKILLS}")
    print(f"  - Top N companies: {config.TOP_N_COMPANIES}")
    print(f"  - Output directory: {output_dir}")
    print()
    
    # Generate all analyses
    print("Generating analyses...")
    generator = AnalysisGenerator(output_dir, config)
    exit_code = generator.generate_all()
    
    if exit_code == 0:
        print()
        print("=" * 60)
        print("✓ Analysis generation completed successfully!")
        print("=" * 60)
        print()
        
        # Read and display index
        index_path = Path(output_dir) / "index.json"
        if index_path.exists():
            with open(index_path, 'r') as f:
                index = json.load(f)
            
            print(f"Generated {index['total_analyses']} analyses:")
            print()
            
            # Group by type
            static = [a for a in index['analyses'] if a['type'] == 'static']
            temporal = [a for a in index['analyses'] if a['type'] == 'temporal']
            
            print(f"Static Analyses ({len(static)}):")
            for analysis in static:
                print(f"  - {analysis['title']} ({analysis['file']})")
            
            print()
            print(f"Temporal Analyses ({len(temporal)}):")
            for analysis in temporal:
                print(f"  - {analysis['title']} ({analysis['file']})")
            
            print()
            print(f"Files available in: {output_dir}")
        
        return 0
    else:
        print()
        print("=" * 60)
        print("✗ Analysis generation failed!")
        print("=" * 60)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
