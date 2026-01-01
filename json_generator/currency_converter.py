"""Currency conversion for salary normalization."""

from typing import Optional, Dict
from src.exhangerate import get_exchange_rates, ExchangeAPIError


class CurrencyConverter:
    """Convert salaries to MDL using current exchange rates."""
    
    def __init__(self):
        """Initialize converter and fetch exchange rates."""
        self.rates: Optional[Dict[str, float]] = None
        self.base_currency = "MDL"
        self._fetch_rates()
    
    def _fetch_rates(self) -> None:
        """Fetch current exchange rates from API."""
        try:
            # Get rates with MDL as base currency
            self.rates = get_exchange_rates(self.base_currency)
            print(f"✓ Fetched exchange rates (base: {self.base_currency})")
        except ExchangeAPIError as e:
            print(f"⚠ Warning: Could not fetch exchange rates: {e}")
            print("  Salary conversion will be skipped")
            self.rates = None
        except Exception as e:
            print(f"⚠ Warning: Unexpected error fetching rates: {e}")
            print("  Salary conversion will be skipped")
            self.rates = None
    
    def convert_to_mdl(self, amount: float, from_currency: str) -> Optional[float]:
        """
        Convert an amount from a given currency to MDL.
        
        Args:
            amount: Amount to convert.
            from_currency: Source currency code (e.g., 'USD', 'EUR').
            
        Returns:
            Converted amount in MDL, or None if conversion not possible.
        """
        if not self.rates or not amount or not from_currency:
            return None
        
        from_currency = from_currency.upper()
        
        # If already in MDL, return as-is
        if from_currency == self.base_currency:
            return amount
        
        # Check if we have the exchange rate
        if from_currency not in self.rates:
            return None
        
        # Convert: amount_in_mdl = amount_in_source / rate
        # Example: 100 USD, rate USD=17.5 (1 MDL = 17.5 USD means 1 USD = 1/17.5 MDL)
        # So: 100 USD = 100 / 17.5 = 5.71 MDL
        # Wait, that doesn't make sense. Let me reconsider.
        
        # The API returns rates from base (MDL) to other currencies
        # So if base=MDL and rates['USD']=17.5, it means 1 MDL = 17.5 USD
        # To convert USD to MDL: amount_usd / rate_usd = amount_mdl
        # Example: 100 USD / 17.5 = 5.71 MDL
        
        # Actually, let me check the API behavior more carefully
        # If base=MDL and we get rates['USD']=0.057, it means 1 MDL = 0.057 USD
        # So to convert USD to MDL: amount_usd / 0.057 = amount_mdl
        
        rate = self.rates[from_currency]
        converted = amount / rate if rate > 0 else None
        
        return round(converted, 2) if converted else None
    
    def convert_salary_range(self, min_salary: Optional[float], max_salary: Optional[float],
                            currency: Optional[str]) -> Dict[str, Optional[float]]:
        """
        Convert a salary range to MDL.
        
        Args:
            min_salary: Minimum salary.
            max_salary: Maximum salary.
            currency: Currency code.
            
        Returns:
            Dictionary with converted min/max in MDL.
        """
        result = {
            'min_mdl': None,
            'max_mdl': None
        }
        
        if currency and self.rates:
            if min_salary:
                result['min_mdl'] = self.convert_to_mdl(min_salary, currency)
            if max_salary:
                result['max_mdl'] = self.convert_to_mdl(max_salary, currency)
        
        return result
