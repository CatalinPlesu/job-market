"""Common aggregation utilities for analyses."""

from collections import defaultdict
from statistics import mean, median
from typing import List, Dict, Any, Callable, Optional


class Aggregator:
    """Common aggregation utilities for analyses."""
    
    # Cache for exchange rates to avoid repeated API calls
    _exchange_rates_cache: Optional[Dict[str, float]] = None
    
    @staticmethod
    def get_exchange_rates() -> Dict[str, float]:
        """
        Get current exchange rates with MDL as base currency.
        Caches the result to avoid repeated API calls.
        
        Returns:
            Dict mapping currency codes to their rate relative to MDL
            e.g., {'USD': 17.5, 'EUR': 19.2, 'MDL': 1.0, ...}
        """
        if Aggregator._exchange_rates_cache is not None:
            return Aggregator._exchange_rates_cache
        
        try:
            from src.exhangerate import get_exchange_rates
            # Fetch rates with MDL as base (so all rates are "X units = 1 MDL")
            rates = get_exchange_rates("MDL")
            Aggregator._exchange_rates_cache = rates
            return rates
        except Exception as e:
            # If exchange rate fetch fails, use fallback rates
            print(f"Warning: Could not fetch exchange rates: {e}")
            print("Using fallback exchange rates")
            # Fallback rates (approximate as of 2024)
            fallback_rates = {
                'MDL': 1.0,
                'USD': 0.056,  # 1 MDL = 0.056 USD, so 1 USD = ~17.8 MDL
                'EUR': 0.051,  # 1 MDL = 0.051 EUR, so 1 EUR = ~19.6 MDL
                'GBP': 0.044,  # 1 MDL = 0.044 GBP, so 1 GBP = ~22.7 MDL
            }
            Aggregator._exchange_rates_cache = fallback_rates
            return fallback_rates
    
    @staticmethod
    def convert_to_mdl(amount: float, currency_code: str) -> float:
        """
        Convert an amount in any currency to MDL.
        
        Args:
            amount: Amount in the source currency
            currency_code: Currency code (e.g., 'USD', 'EUR', 'MDL')
            
        Returns:
            Amount converted to MDL
        """
        if not amount or not currency_code:
            return amount
        
        currency_code = currency_code.upper()
        
        # If already in MDL, no conversion needed
        if currency_code == 'MDL':
            return amount
        
        rates = Aggregator.get_exchange_rates()
        
        # rates[currency] gives us how many of that currency = 1 MDL
        # So to convert FROM that currency TO MDL: amount / rates[currency]
        if currency_code in rates:
            rate = rates[currency_code]
            if rate > 0:
                return amount / rate
        
        # If currency not found, return original amount
        # (better than crashing)
        print(f"Warning: Currency {currency_code} not found in exchange rates, using original value")
        return amount
    
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
        """
        Get average salary from a job record, converted to MDL.
        
        Args:
            job: JobDetail record with salary and currency information
            
        Returns:
            Average salary in MDL, or None if no salary data
        """
        # Calculate average in original currency
        avg_salary = None
        if job.max_salary and job.min_salary:
            avg_salary = float((job.min_salary + job.max_salary) / 2)
        elif job.min_salary:
            avg_salary = float(job.min_salary)
        elif job.max_salary:
            avg_salary = float(job.max_salary)
        
        if not avg_salary:
            return None
        
        # Get currency code - default to MDL if not specified
        # This is a reasonable default for Moldova job market data
        currency_code = 'MDL'
        if job.salary_currency and hasattr(job.salary_currency, 'code'):
            currency_code = job.salary_currency.code
        
        # Convert to MDL
        return Aggregator.convert_to_mdl(avg_salary, currency_code)
    
    @staticmethod
    def sort_checks_by_date(checks):
        """Sort job checks by check_date."""
        return sorted(checks, key=lambda c: c.check_date)
    
    @staticmethod
    def get_period_key(dt, granularity):
        """
        Convert datetime to period key for bucketing.
        
        Args:
            dt: datetime or date object
            granularity: 'daily', 'weekly', or 'monthly'
        
        Returns:
            String period key (e.g., '2026-01', '2026-W01', '2026-01-01')
        """
        from datetime import datetime, date
        
        # Convert date to datetime if needed for week calculation
        if granularity == 'monthly':
            return dt.strftime('%Y-%m')
        elif granularity == 'weekly':
            # Ensure we have a datetime for week calculation
            if isinstance(dt, date) and not isinstance(dt, datetime):
                dt = datetime.combine(dt, datetime.min.time())
            return dt.strftime('%Y-W%U')
        else:  # daily
            return dt.strftime('%Y-%m-%d')
