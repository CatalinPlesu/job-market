"""Base class for all analyses."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class BaseAnalysis(ABC):
    """Base class for all analyses."""
    
    def __init__(self, scrape_db, data_db, config):
        """
        Initialize analysis.
        
        Args:
            scrape_db: SQLAlchemy session for scrape.db
            data_db: SQLAlchemy session for data.db
            config: AnalysisConfig instance
        """
        self.scrape_db = scrape_db
        self.data_db = data_db
        self.config = config
        self.generated_at = datetime.utcnow()
    
    @property
    @abstractmethod
    def analysis_id(self) -> str:
        """Unique identifier for this analysis."""
        pass
    
    @property
    @abstractmethod
    def title(self) -> str:
        """Human-readable title."""
        pass
    
    @property
    def is_temporal(self) -> bool:
        """Whether this analysis includes time series data."""
        return False
    
    @abstractmethod
    def compute(self) -> Dict[str, Any]:
        """
        Compute the analysis.
        
        Returns:
            Dictionary with analysis results.
        """
        pass
    
    def to_json(self) -> Dict[str, Any]:
        """
        Convert analysis to JSON format.
        Includes metadata and results.
        """
        data = self.compute()
        
        return {
            'version': '1.0',
            'analysis_id': self.analysis_id,
            'title': self.title,
            'generated_at': self.generated_at.isoformat() + 'Z',
            'type': 'temporal' if self.is_temporal else 'static',
            'data': data,
            'visualization_hints': self.get_visualization_hints()
        }
    
    def get_visualization_hints(self) -> Dict[str, Any]:
        """
        Suggest visualization approaches for frontend.
        Override in subclasses for custom hints.
        """
        return {
            'chart_types': ['table'],
            'recommended_chart': 'table'
        }
