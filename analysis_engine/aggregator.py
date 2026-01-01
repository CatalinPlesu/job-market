"""Common aggregation utilities for analyses."""

from collections import defaultdict
from statistics import mean, median
from typing import List, Dict, Any, Callable


class Aggregator:
    """Common aggregation utilities for analyses."""
    
    @staticmethod
    def group_by(items, key_func: Callable):
        """Group items by a key function."""
        groups = defaultdict(list)
        for item in items:
            key = key_func(item)
            if key:
                groups[key].append(item)
        return dict(groups)
    
    @staticmethod
    def compute_stats(values: List[float]) -> Dict[str, float]:
        """Compute common statistics for a list of values."""
        if not values:
            return {}
        
        stats = {
            'count': len(values),
            'sum': sum(values),
            'average': mean(values),
            'median': median(values),
            'min': min(values),
            'max': max(values)
        }
        
        # Add quartiles if enough data
        if len(values) >= 4:
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            stats['percentile_25'] = sorted_vals[n // 4]
            stats['percentile_75'] = sorted_vals[3 * n // 4]
        
        return stats
    
    @staticmethod
    def remove_outliers(values: List[float], threshold: float = 3.0) -> List[float]:
        """Remove outliers using z-score method."""
        if len(values) < 3:
            return values
        
        avg = mean(values)
        variance = sum((x - avg) ** 2 for x in values) / len(values)
        std = variance ** 0.5
        
        if std == 0:
            return values
        
        return [
            v for v in values 
            if abs((v - avg) / std) <= threshold
        ]
    
    @staticmethod
    def bucket_by_range(values: List[float], ranges: List[tuple]) -> List[Dict[str, Any]]:
        """Bucket values into ranges."""
        buckets = []
        total = len(values)
        
        for min_val, max_val in ranges:
            count = sum(1 for v in values if min_val <= v < max_val)
            if count > 0:
                label = f'{min_val}-{max_val}' if max_val != float('inf') else f'{min_val}+'
                buckets.append({
                    'range': label,
                    'min': min_val,
                    'max': max_val if max_val != float('inf') else None,
                    'count': count,
                    'percentage': round((count / total) * 100, 2) if total > 0 else 0
                })
        
        return buckets
    
    @staticmethod
    def get_average_salary(job):
        """Get average salary from a job record."""
        if job.max_salary and job.min_salary:
            return float((job.min_salary + job.max_salary) / 2)
        elif job.min_salary:
            return float(job.min_salary)
        elif job.max_salary:
            return float(job.max_salary)
        return None
    
    @staticmethod
    def sort_checks_by_date(checks):
        """Sort job checks by check_date."""
        return sorted(checks, key=lambda c: c.check_date)
