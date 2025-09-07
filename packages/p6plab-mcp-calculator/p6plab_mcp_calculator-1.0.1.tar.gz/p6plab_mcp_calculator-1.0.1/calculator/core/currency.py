"""
Currency conversion module for the Scientific Calculator MCP Server.

This module provides optional currency conversion capabilities with privacy controls,
fallback mechanisms, and rate caching. Currency conversion is disabled by default
and requires explicit user enablement via environment variables.
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests
from decimal import Decimal

from calculator.models.errors import CalculatorError, ValidationError


class CurrencyError(CalculatorError):
    """Error for currency conversion operations."""
    pass


# Privacy-first design: Currency conversion is disabled by default
CURRENCY_ENABLED = os.getenv("CALCULATOR_ENABLE_CURRENCY_CONVERSION", "false").lower() == "true"
CURRENCY_API_KEY = os.getenv("CALCULATOR_CURRENCY_API_KEY", "")
CACHE_DURATION_HOURS = int(os.getenv("CALCULATOR_CURRENCY_CACHE_HOURS", "24"))

# Fallback exchange rates (approximate, for offline use only)
FALLBACK_RATES = {
    "USD": 1.0,  # Base currency
    "EUR": 0.85,
    "GBP": 0.73,
    "JPY": 110.0,
    "CAD": 1.25,
    "AUD": 1.35,
    "CHF": 0.92,
    "CNY": 6.45,
    "INR": 74.5,
    "BRL": 5.2,
    "RUB": 75.0,
    "KRW": 1180.0,
    "MXN": 20.0,
    "SGD": 1.35,
    "HKD": 7.8,
    "NOK": 8.5,
    "SEK": 8.8,
    "DKK": 6.3,
    "PLN": 3.9,
    "CZK": 21.5,
    "HUF": 295.0,
    "ILS": 3.2,
    "NZD": 1.4,
    "ZAR": 14.5,
    "TRY": 8.5,
    "THB": 31.0,
    "MYR": 4.1,
    "PHP": 49.0,
    "IDR": 14300.0,
    "VND": 23000.0,
}

# Simple in-memory cache for exchange rates
_rate_cache = {}
_cache_timestamp = None


def _check_currency_enabled():
    """Check if currency conversion is enabled."""
    if not CURRENCY_ENABLED:
        raise CurrencyError(
            "Currency conversion is disabled. "
            "Set CALCULATOR_ENABLE_CURRENCY_CONVERSION=true to enable this feature."
        )


def _validate_currency_code(currency: str) -> str:
    """Validate and normalize currency code."""
    if not currency or not isinstance(currency, str):
        raise ValidationError("Currency code must be a non-empty string")
    
    currency_upper = currency.upper().strip()
    
    if len(currency_upper) != 3:
        raise ValidationError("Currency code must be exactly 3 characters")
    
    if not currency_upper.isalpha():
        raise ValidationError("Currency code must contain only letters")
    
    return currency_upper


def _validate_amount(amount: float) -> float:
    """Validate currency amount."""
    try:
        amount_val = float(amount)
        if amount_val < 0:
            raise ValidationError("Amount must be non-negative")
        if amount_val > 1e15:
            raise ValidationError("Amount too large")
        return amount_val
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid amount: {e}") from e


def _is_cache_valid() -> bool:
    """Check if the current cache is still valid."""
    global _cache_timestamp
    if _cache_timestamp is None or not _rate_cache:
        return False
    
    cache_age = datetime.now() - _cache_timestamp
    return cache_age < timedelta(hours=CACHE_DURATION_HOURS)


def _fetch_rates_from_api() -> Optional[Dict[str, float]]:
    """Fetch exchange rates from external API."""
    if not CURRENCY_API_KEY:
        return None
    
    try:
        # Example API call (would need to be adapted for specific API)
        # This is a placeholder - in real implementation, you'd use a specific API
        url = f"https://api.exchangerate-api.com/v4/latest/USD"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if "rates" in data:
            return data["rates"]
        
        return None
        
    except Exception as e:
        # Log the error but don't raise - we'll fall back to cached or fallback rates
        return None


def _get_exchange_rates() -> Dict[str, float]:
    """Get exchange rates with fallback mechanisms."""
    global _rate_cache, _cache_timestamp
    
    # Check if cache is valid
    if _is_cache_valid():
        return _rate_cache
    
    # Try to fetch from API if API key is provided
    if CURRENCY_API_KEY:
        api_rates = _fetch_rates_from_api()
        if api_rates:
            _rate_cache = api_rates
            _cache_timestamp = datetime.now()
            return _rate_cache
    
    # Fall back to cached rates if available
    if _rate_cache:
        return _rate_cache
    
    # Final fallback to hardcoded rates
    _rate_cache = FALLBACK_RATES.copy()
    _cache_timestamp = datetime.now()
    return _rate_cache


def convert_currency(amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Convert currency with privacy controls and fallback mechanisms.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code (3-letter ISO code)
        to_currency: Target currency code (3-letter ISO code)
    """
    try:
        # Check if currency conversion is enabled
        _check_currency_enabled()
        
        # Validate inputs
        amount_val = _validate_amount(amount)
        from_curr = _validate_currency_code(from_currency)
        to_curr = _validate_currency_code(to_currency)
        
        # Handle same currency conversion
        if from_curr == to_curr:
            return {
                "converted_amount": amount_val,
                "original_amount": amount_val,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "exchange_rate": 1.0,
                "rate_source": "same_currency",
                "timestamp": datetime.now().isoformat(),
                "operation": "currency_conversion"
            }
        
        # Get exchange rates
        try:
            rates = _get_exchange_rates()
        except Exception as e:
            raise CurrencyError(f"Unable to fetch exchange rates: {e}")
        
        # Check if currencies are supported
        if from_curr not in rates:
            available_currencies = sorted(rates.keys())
            raise CurrencyError(
                f"Currency '{from_curr}' not supported. "
                f"Available currencies: {', '.join(available_currencies[:10])}..."
            )
        
        if to_curr not in rates:
            available_currencies = sorted(rates.keys())
            raise CurrencyError(
                f"Currency '{to_curr}' not supported. "
                f"Available currencies: {', '.join(available_currencies[:10])}..."
            )
        
        # Calculate conversion
        # Most APIs provide rates relative to USD, so we convert via USD
        if from_curr == "USD":
            exchange_rate = rates[to_curr]
            converted_amount = amount_val * exchange_rate
        elif to_curr == "USD":
            exchange_rate = 1.0 / rates[from_curr]
            converted_amount = amount_val * exchange_rate
        else:
            # Convert from_currency -> USD -> to_currency
            usd_rate = 1.0 / rates[from_curr]
            target_rate = rates[to_curr]
            exchange_rate = usd_rate * target_rate
            converted_amount = amount_val * exchange_rate
        
        # Determine rate source
        if _cache_timestamp and (datetime.now() - _cache_timestamp) < timedelta(hours=1):
            if CURRENCY_API_KEY:
                rate_source = "api_recent"
            else:
                rate_source = "fallback_recent"
        else:
            rate_source = "cached_or_fallback"
        
        return {
            "converted_amount": round(converted_amount, 4),
            "original_amount": amount_val,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "exchange_rate": round(exchange_rate, 6),
            "rate_source": rate_source,
            "timestamp": datetime.now().isoformat(),
            "cache_age_hours": (datetime.now() - _cache_timestamp).total_seconds() / 3600 if _cache_timestamp else None,
            "operation": "currency_conversion"
        }
        
    except Exception as e:
        raise CurrencyError(f"Error converting currency: {e}") from e


def get_supported_currencies() -> Dict[str, Any]:
    """Get list of supported currencies."""
    try:
        _check_currency_enabled()
        
        rates = _get_exchange_rates()
        currencies = sorted(rates.keys())
        
        return {
            "currencies": currencies,
            "count": len(currencies),
            "base_currency": "USD",
            "rate_source": "api" if CURRENCY_API_KEY else "fallback",
            "cache_enabled": True,
            "cache_duration_hours": CACHE_DURATION_HOURS,
            "operation": "get_supported_currencies"
        }
        
    except Exception as e:
        raise CurrencyError(f"Error getting supported currencies: {e}") from e


def get_exchange_rate(from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Get exchange rate between two currencies without conversion.
    
    Args:
        from_currency: Source currency code
        to_currency: Target currency code
    """
    try:
        _check_currency_enabled()
        
        from_curr = _validate_currency_code(from_currency)
        to_curr = _validate_currency_code(to_currency)
        
        # Handle same currency
        if from_curr == to_curr:
            return {
                "exchange_rate": 1.0,
                "from_currency": from_curr,
                "to_currency": to_curr,
                "rate_source": "same_currency",
                "timestamp": datetime.now().isoformat(),
                "operation": "get_exchange_rate"
            }
        
        # Get rates and calculate exchange rate
        rates = _get_exchange_rates()
        
        if from_curr not in rates or to_curr not in rates:
            available_currencies = sorted(rates.keys())
            raise CurrencyError(
                f"One or both currencies not supported. "
                f"Available currencies: {', '.join(available_currencies[:10])}..."
            )
        
        # Calculate exchange rate
        if from_curr == "USD":
            exchange_rate = rates[to_curr]
        elif to_curr == "USD":
            exchange_rate = 1.0 / rates[from_curr]
        else:
            usd_rate = 1.0 / rates[from_curr]
            target_rate = rates[to_curr]
            exchange_rate = usd_rate * target_rate
        
        return {
            "exchange_rate": round(exchange_rate, 6),
            "from_currency": from_curr,
            "to_currency": to_curr,
            "rate_source": "api" if CURRENCY_API_KEY else "fallback",
            "timestamp": datetime.now().isoformat(),
            "cache_age_hours": (datetime.now() - _cache_timestamp).total_seconds() / 3600 if _cache_timestamp else None,
            "operation": "get_exchange_rate"
        }
        
    except Exception as e:
        raise CurrencyError(f"Error getting exchange rate: {e}") from e


def convert_multiple_currencies(amount: float, from_currency: str, 
                               to_currencies: List[str]) -> Dict[str, Any]:
    """Convert amount to multiple target currencies.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currencies: List of target currency codes
    """
    try:
        _check_currency_enabled()
        
        if not to_currencies:
            raise ValidationError("Target currencies list cannot be empty")
        
        if len(to_currencies) > 20:
            raise ValidationError("Too many target currencies (maximum 20)")
        
        amount_val = _validate_amount(amount)
        from_curr = _validate_currency_code(from_currency)
        
        conversions = {}
        errors = {}
        
        for to_currency in to_currencies:
            try:
                result = convert_currency(amount_val, from_curr, to_currency)
                conversions[to_currency] = {
                    "converted_amount": result["converted_amount"],
                    "exchange_rate": result["exchange_rate"]
                }
            except Exception as e:
                errors[to_currency] = str(e)
        
        return {
            "conversions": conversions,
            "errors": errors,
            "original_amount": amount_val,
            "from_currency": from_curr,
            "successful_conversions": len(conversions),
            "failed_conversions": len(errors),
            "timestamp": datetime.now().isoformat(),
            "operation": "convert_multiple_currencies"
        }
        
    except Exception as e:
        raise CurrencyError(f"Error in multiple currency conversion: {e}") from e


def clear_currency_cache() -> Dict[str, Any]:
    """Clear the currency rate cache."""
    global _rate_cache, _cache_timestamp
    
    try:
        _check_currency_enabled()
        
        cache_size = len(_rate_cache)
        cache_age = (datetime.now() - _cache_timestamp).total_seconds() / 3600 if _cache_timestamp else None
        
        _rate_cache.clear()
        _cache_timestamp = None
        
        return {
            "cache_cleared": True,
            "previous_cache_size": cache_size,
            "previous_cache_age_hours": cache_age,
            "timestamp": datetime.now().isoformat(),
            "operation": "clear_currency_cache"
        }
        
    except Exception as e:
        raise CurrencyError(f"Error clearing currency cache: {e}") from e


def get_currency_info() -> Dict[str, Any]:
    """Get information about currency conversion configuration and status."""
    return {
        "currency_enabled": CURRENCY_ENABLED,
        "api_key_configured": bool(CURRENCY_API_KEY),
        "cache_duration_hours": CACHE_DURATION_HOURS,
        "cache_size": len(_rate_cache),
        "cache_timestamp": _cache_timestamp.isoformat() if _cache_timestamp else None,
        "cache_valid": _is_cache_valid(),
        "fallback_currencies_count": len(FALLBACK_RATES),
        "privacy_note": "Currency conversion is disabled by default for privacy. Enable via CALCULATOR_ENABLE_CURRENCY_CONVERSION=true",
        "operation": "get_currency_info"
    }