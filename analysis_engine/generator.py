"""Main analysis generator that orchestrates all analyses."""

import json
import os
from pathlib import Path
from datetime import datetime

from .config import AnalysisConfig
from .static.salary import (
    SalaryOverviewAnalysis, SalaryByFunctionAnalysis,
    SalaryBySeniorityAnalysis, SalaryByLocationAnalysis,
    SalaryByCompanySizeAnalysis, SalaryByEducationAnalysis
)
from .static.skills import (
    SkillsDemandAnalysis, SkillsSalaryAnalysis, SkillCombinationsAnalysis
)
from .static.employment import (
    EmploymentTypesAnalysis, RemoteWorkAnalysis,
    BenefitsAnalysis, RequirementsAnalysis
)
from .static.companies import TopCompaniesAnalysis
from .temporal.posting_trends import PostingTrendsAnalysis
from .temporal.salary_trends import SalaryTrendsAnalysis
from .temporal.skills_trends import SkillsTrendsAnalysis
from .temporal.remote_trends import RemoteTrendsAnalysis
from .temporal.market_health import JobDurationAnalysis, MarketHealthAnalysis
from .hierarchy import SalaryHierarchyAnalysis

from src.scrape_database import ScrapeSessionLocal
from src.data_database import DataSessionLocal


class AnalysisGenerator:
    """Main generator for all analyses."""
    
    def __init__(self, output_dir: str = "pages/api/analysis", config=None):
        """
        Initialize the analysis generator.
        
        Args:
            output_dir: Directory to write JSON files
            config: AnalysisConfig instance (defaults to AnalysisConfig())
        """
        self.output_dir = Path(output_dir)
        self.config = config or AnalysisConfig()
        
        # Database sessions
        self.scrape_db = None
        self.data_db = None
        
        # All analyses to generate
        self.analyses = [
            # Static analyses
            SalaryOverviewAnalysis,
            SalaryByFunctionAnalysis,
            SalaryBySeniorityAnalysis,
            SalaryByLocationAnalysis,
            SalaryByCompanySizeAnalysis,
            SalaryByEducationAnalysis,
            SkillsDemandAnalysis,
            SkillsSalaryAnalysis,
            SkillCombinationsAnalysis,
            EmploymentTypesAnalysis,
            RemoteWorkAnalysis,
            BenefitsAnalysis,
            RequirementsAnalysis,
            TopCompaniesAnalysis,
            # Temporal analyses
            PostingTrendsAnalysis,
            SalaryTrendsAnalysis,
            SkillsTrendsAnalysis,
            RemoteTrendsAnalysis,
            JobDurationAnalysis,
            MarketHealthAnalysis,
            # Hierarchy analysis
            SalaryHierarchyAnalysis,
        ]
    
    def generate_all(self):
        """Generate all analyses and write to JSON files."""
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database sessions
        self.scrape_db = ScrapeSessionLocal()
        self.data_db = DataSessionLocal()
        
        try:
            results = []
            
            print(f"Generating {len(self.analyses)} analyses...")
            
            for i, AnalysisClass in enumerate(self.analyses, 1):
                try:
                    print(f"[{i}/{len(self.analyses)}] Generating {AnalysisClass.__name__}...")
                    
                    analysis = AnalysisClass(self.scrape_db, self.data_db, self.config)
                    result = analysis.to_json()
                    
                    # Write to file
                    filename = f"{analysis.analysis_id}.json"
                    filepath = self.output_dir / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    print(f"  ✓ Written to {filepath}")
                    
                    # Add to results for index
                    results.append({
                        'id': analysis.analysis_id,
                        'title': analysis.title,
                        'type': result['type'],
                        'file': filename
                    })
                    
                except Exception as e:
                    print(f"  ✗ Error: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Generate index.json
            self._generate_index(results)
            
            print(f"\n✓ Successfully generated {len(results)} analyses")
            return 0
            
        except Exception as e:
            print(f"✗ Error during generation: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1
            
        finally:
            # Close database sessions
            if self.scrape_db:
                self.scrape_db.close()
            if self.data_db:
                self.data_db.close()
    
    def _generate_index(self, results):
        """Generate index.json with list of available analyses."""
        index_data = {
            'version': '1.0',
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'total_analyses': len(results),
            'analyses': results
        }
        
        index_path = self.output_dir / 'index.json'
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Generated index: {index_path}")
