"""Data sanitization for privacy and security."""

from typing import Dict, Any, Set
from pathlib import Path


class DataSanitizer:
    """Remove sensitive information before generating public JSON."""
    
    EXCLUDED_FIELDS = [
        'contact_emails',
        'contact_phones',
        'contact_person',
        'contact_person_id'
    ]
    
    def __init__(self, blacklist_file: str = None):
        """
        Initialize sanitizer.
        
        Args:
            blacklist_file: Path to company blacklist file (optional).
        """
        self.blacklist = self._load_blacklist(blacklist_file) if blacklist_file else set()
    
    def _load_blacklist(self, filepath: str) -> Set[str]:
        """
        Load company blacklist from file.
        
        Args:
            filepath: Path to blacklist file.
            
        Returns:
            Set of company names to anonymize.
        """
        path = Path(filepath)
        if not path.exists():
            return set()
        
        with open(path, 'r', encoding='utf-8') as f:
            return {line.strip() for line in f if line.strip()}
    
    def sanitize_job(self, job_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive fields from job dictionary.
        
        Args:
            job_dict: Job data as dictionary.
            
        Returns:
            Sanitized job dictionary.
        """
        # Create a copy to avoid modifying original
        sanitized = {k: v for k, v in job_dict.items() 
                     if k not in self.EXCLUDED_FIELDS}
        
        # Anonymize blacklisted companies
        if sanitized.get('company') in self.blacklist:
            sanitized['company'] = 'Confidential'
        
        return sanitized
    
    def should_aggregate(self, category_count: int, min_count: int = 10) -> bool:
        """
        Determine if category should be aggregated to 'Other'.
        
        Args:
            category_count: Number of items in category.
            min_count: Minimum count threshold.
            
        Returns:
            True if should aggregate, False otherwise.
        """
        return category_count < min_count
