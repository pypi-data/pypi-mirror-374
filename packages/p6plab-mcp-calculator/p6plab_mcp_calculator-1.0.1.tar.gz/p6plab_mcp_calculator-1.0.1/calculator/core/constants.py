"""
Mathematical and physical constants module for the Scientific Calculator MCP Server.

This module provides access to mathematical constants, physical constants,
and common formulas with high precision values and descriptions.
"""

import math
from typing import Dict, Any, List, Optional
from decimal import Decimal, getcontext

from calculator.models.errors import CalculatorError, ValidationError


class ConstantsError(CalculatorError):
    """Error for constants operations."""
    pass


# Set high precision for constants
getcontext().prec = 50

# Mathematical Constants
MATHEMATICAL_CONSTANTS = {
    "pi": {
        "value": math.pi,
        "high_precision": "3.1415926535897932384626433832795028841971693993751",
        "symbol": "π",
        "description": "The ratio of a circle's circumference to its diameter",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "e": {
        "value": math.e,
        "high_precision": "2.7182818284590452353602874713526624977572470937000",
        "symbol": "e",
        "description": "Euler's number, the base of natural logarithms",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "phi": {
        "value": (1 + math.sqrt(5)) / 2,
        "high_precision": "1.6180339887498948482045868343656381177203091798058",
        "symbol": "φ",
        "description": "Golden ratio, the limit of the ratio of consecutive Fibonacci numbers",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "sqrt2": {
        "value": math.sqrt(2),
        "high_precision": "1.4142135623730950488016887242096980785696718753769",
        "symbol": "√2",
        "description": "Square root of 2, Pythagoras' constant",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "sqrt3": {
        "value": math.sqrt(3),
        "high_precision": "1.7320508075688772935274463415058723669428052538104",
        "symbol": "√3",
        "description": "Square root of 3, Theodorus' constant",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "euler_gamma": {
        "value": 0.5772156649015329,
        "high_precision": "0.5772156649015328606065120900824024310421593359399",
        "symbol": "γ",
        "description": "Euler-Mascheroni constant, limiting difference between harmonic series and natural logarithm",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "catalan": {
        "value": 0.9159655941772190,
        "high_precision": "0.9159655941772190150546035149323841107741493742817",
        "symbol": "G",
        "description": "Catalan's constant, appears in combinatorics and number theory",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "apery": {
        "value": 1.2020569031595943,
        "high_precision": "1.2020569031595942853997381615114499907649862923405",
        "symbol": "ζ(3)",
        "description": "Apéry's constant, the value of the Riemann zeta function at 3",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "ln2": {
        "value": math.log(2),
        "high_precision": "0.6931471805599453094172321214581765680755001343602",
        "symbol": "ln(2)",
        "description": "Natural logarithm of 2",
        "category": "mathematical",
        "unit": "dimensionless"
    },
    "ln10": {
        "value": math.log(10),
        "high_precision": "2.3025850929940456840179914546843642076011014886288",
        "symbol": "ln(10)",
        "description": "Natural logarithm of 10",
        "category": "mathematical",
        "unit": "dimensionless"
    }
}

# Physical Constants (CODATA 2018 values)
PHYSICAL_CONSTANTS = {
    "c": {
        "value": 299792458,
        "high_precision": "299792458",
        "symbol": "c",
        "description": "Speed of light in vacuum",
        "category": "physical",
        "unit": "m/s"
    },
    "h": {
        "value": 6.62607015e-34,
        "high_precision": "6.62607015e-34",
        "symbol": "h",
        "description": "Planck constant",
        "category": "physical",
        "unit": "J⋅s"
    },
    "hbar": {
        "value": 1.054571817e-34,
        "high_precision": "1.054571817e-34",
        "symbol": "ℏ",
        "description": "Reduced Planck constant (h/2π)",
        "category": "physical",
        "unit": "J⋅s"
    },
    "k": {
        "value": 1.380649e-23,
        "high_precision": "1.380649e-23",
        "symbol": "k",
        "description": "Boltzmann constant",
        "category": "physical",
        "unit": "J/K"
    },
    "Na": {
        "value": 6.02214076e23,
        "high_precision": "6.02214076e23",
        "symbol": "Nₐ",
        "description": "Avogadro constant",
        "category": "physical",
        "unit": "mol⁻¹"
    },
    "R": {
        "value": 8.314462618,
        "high_precision": "8.314462618",
        "symbol": "R",
        "description": "Universal gas constant",
        "category": "physical",
        "unit": "J/(mol⋅K)"
    },
    "e_charge": {
        "value": 1.602176634e-19,
        "high_precision": "1.602176634e-19",
        "symbol": "e",
        "description": "Elementary charge",
        "category": "physical",
        "unit": "C"
    },
    "me": {
        "value": 9.1093837015e-31,
        "high_precision": "9.1093837015e-31",
        "symbol": "mₑ",
        "description": "Electron rest mass",
        "category": "physical",
        "unit": "kg"
    },
    "mp": {
        "value": 1.67262192369e-27,
        "high_precision": "1.67262192369e-27",
        "symbol": "mₚ",
        "description": "Proton rest mass",
        "category": "physical",
        "unit": "kg"
    },
    "mn": {
        "value": 1.67492749804e-27,
        "high_precision": "1.67492749804e-27",
        "symbol": "mₙ",
        "description": "Neutron rest mass",
        "category": "physical",
        "unit": "kg"
    },
    "G": {
        "value": 6.67430e-11,
        "high_precision": "6.67430e-11",
        "symbol": "G",
        "description": "Gravitational constant",
        "category": "physical",
        "unit": "m³/(kg⋅s²)"
    },
    "g": {
        "value": 9.80665,
        "high_precision": "9.80665",
        "symbol": "g",
        "description": "Standard acceleration due to gravity",
        "category": "physical",
        "unit": "m/s²"
    },
    "epsilon0": {
        "value": 8.8541878128e-12,
        "high_precision": "8.8541878128e-12",
        "symbol": "ε₀",
        "description": "Vacuum permittivity",
        "category": "physical",
        "unit": "F/m"
    },
    "mu0": {
        "value": 1.25663706212e-6,
        "high_precision": "1.25663706212e-6",
        "symbol": "μ₀",
        "description": "Vacuum permeability",
        "category": "physical",
        "unit": "H/m"
    },
    "alpha": {
        "value": 7.2973525693e-3,
        "high_precision": "7.2973525693e-3",
        "symbol": "α",
        "description": "Fine-structure constant",
        "category": "physical",
        "unit": "dimensionless"
    },
    "sigma": {
        "value": 5.670374419e-8,
        "high_precision": "5.670374419e-8",
        "symbol": "σ",
        "description": "Stefan-Boltzmann constant",
        "category": "physical",
        "unit": "W/(m²⋅K⁴)"
    }
}

# Astronomical Constants
ASTRONOMICAL_CONSTANTS = {
    "au": {
        "value": 149597870700,
        "high_precision": "149597870700",
        "symbol": "AU",
        "description": "Astronomical unit, mean Earth-Sun distance",
        "category": "astronomical",
        "unit": "m"
    },
    "ly": {
        "value": 9.4607304725808e15,
        "high_precision": "9.4607304725808e15",
        "symbol": "ly",
        "description": "Light-year, distance light travels in one year",
        "category": "astronomical",
        "unit": "m"
    },
    "pc": {
        "value": 3.0856775814913673e16,
        "high_precision": "3.0856775814913673e16",
        "symbol": "pc",
        "description": "Parsec, astronomical unit of length",
        "category": "astronomical",
        "unit": "m"
    },
    "M_sun": {
        "value": 1.98847e30,
        "high_precision": "1.98847e30",
        "symbol": "M☉",
        "description": "Solar mass",
        "category": "astronomical",
        "unit": "kg"
    },
    "R_sun": {
        "value": 6.957e8,
        "high_precision": "6.957e8",
        "symbol": "R☉",
        "description": "Solar radius",
        "category": "astronomical",
        "unit": "m"
    },
    "M_earth": {
        "value": 5.9722e24,
        "high_precision": "5.9722e24",
        "symbol": "M⊕",
        "description": "Earth mass",
        "category": "astronomical",
        "unit": "kg"
    },
    "R_earth": {
        "value": 6.3781e6,
        "high_precision": "6.3781e6",
        "symbol": "R⊕",
        "description": "Earth radius (mean)",
        "category": "astronomical",
        "unit": "m"
    }
}

# Combine all constants
ALL_CONSTANTS = {
    **MATHEMATICAL_CONSTANTS,
    **PHYSICAL_CONSTANTS,
    **ASTRONOMICAL_CONSTANTS
}


def get_constant(name: str, precision: str = "standard") -> Dict[str, Any]:
    """Get a constant by name with specified precision.
    
    Args:
        name: Name of the constant
        precision: "standard" for float precision, "high" for high precision string
    """
    try:
        name_lower = name.lower().strip()
        
        if name_lower not in ALL_CONSTANTS:
            available_constants = sorted(ALL_CONSTANTS.keys())
            raise ConstantsError(
                f"Unknown constant: {name}. "
                f"Available constants: {', '.join(available_constants[:10])}..."
            )
        
        constant_info = ALL_CONSTANTS[name_lower].copy()
        
        if precision == "high":
            constant_info["requested_value"] = constant_info["high_precision"]
        else:
            constant_info["requested_value"] = constant_info["value"]
        
        constant_info["precision_type"] = precision
        constant_info["name"] = name_lower
        constant_info["operation"] = "get_constant"
        
        return constant_info
        
    except Exception as e:
        raise ConstantsError(f"Error getting constant: {e}") from e


def list_constants(category: Optional[str] = None) -> Dict[str, Any]:
    """List available constants, optionally filtered by category.
    
    Args:
        category: Optional category filter ("mathematical", "physical", "astronomical")
    """
    try:
        if category:
            category_lower = category.lower()
            valid_categories = ["mathematical", "physical", "astronomical"]
            if category_lower not in valid_categories:
                raise ValidationError(f"Invalid category: {category}. Valid categories: {valid_categories}")
            
            filtered_constants = {
                name: info for name, info in ALL_CONSTANTS.items()
                if info["category"] == category_lower
            }
        else:
            filtered_constants = ALL_CONSTANTS
        
        # Create summary
        constants_list = []
        for name, info in filtered_constants.items():
            constants_list.append({
                "name": name,
                "symbol": info["symbol"],
                "description": info["description"],
                "category": info["category"],
                "unit": info["unit"],
                "value": info["value"]
            })
        
        # Sort by category then name
        constants_list.sort(key=lambda x: (x["category"], x["name"]))
        
        return {
            "constants": constants_list,
            "count": len(constants_list),
            "category_filter": category,
            "categories": ["mathematical", "physical", "astronomical"],
            "operation": "list_constants"
        }
        
    except Exception as e:
        raise ConstantsError(f"Error listing constants: {e}") from e


def search_constants(query: str) -> Dict[str, Any]:
    """Search constants by name, symbol, or description.
    
    Args:
        query: Search query string
    """
    try:
        if not query or len(query.strip()) < 2:
            raise ValidationError("Search query must be at least 2 characters")
        
        query_lower = query.lower().strip()
        matches = []
        
        for name, info in ALL_CONSTANTS.items():
            # Search in name, symbol, and description
            if (query_lower in name.lower() or 
                query_lower in info["symbol"].lower() or 
                query_lower in info["description"].lower()):
                
                matches.append({
                    "name": name,
                    "symbol": info["symbol"],
                    "description": info["description"],
                    "category": info["category"],
                    "unit": info["unit"],
                    "value": info["value"]
                })
        
        # Sort by relevance (exact name match first, then symbol, then description)
        def relevance_score(match):
            name_match = query_lower == match["name"].lower()
            symbol_match = query_lower == match["symbol"].lower()
            name_contains = query_lower in match["name"].lower()
            symbol_contains = query_lower in match["symbol"].lower()
            
            if name_match: return 0
            elif symbol_match: return 1
            elif name_contains: return 2
            elif symbol_contains: return 3
            else: return 4
        
        matches.sort(key=relevance_score)
        
        return {
            "matches": matches,
            "count": len(matches),
            "query": query,
            "operation": "search_constants"
        }
        
    except Exception as e:
        raise ConstantsError(f"Error searching constants: {e}") from e


def get_constants_by_category(category: str) -> Dict[str, Any]:
    """Get all constants in a specific category.
    
    Args:
        category: Category name ("mathematical", "physical", "astronomical")
    """
    try:
        return list_constants(category)
        
    except Exception as e:
        raise ConstantsError(f"Error getting constants by category: {e}") from e


def compare_constants(names: List[str]) -> Dict[str, Any]:
    """Compare multiple constants side by side.
    
    Args:
        names: List of constant names to compare
    """
    try:
        if not names:
            raise ValidationError("Must provide at least one constant name")
        
        if len(names) > 10:
            raise ValidationError("Too many constants to compare (maximum 10)")
        
        comparisons = []
        errors = []
        
        for name in names:
            try:
                constant_info = get_constant(name)
                comparisons.append({
                    "name": name,
                    "symbol": constant_info["symbol"],
                    "value": constant_info["value"],
                    "high_precision": constant_info["high_precision"],
                    "description": constant_info["description"],
                    "category": constant_info["category"],
                    "unit": constant_info["unit"]
                })
            except Exception as e:
                errors.append({"name": name, "error": str(e)})
        
        return {
            "comparisons": comparisons,
            "errors": errors,
            "successful_comparisons": len(comparisons),
            "failed_comparisons": len(errors),
            "operation": "compare_constants"
        }
        
    except Exception as e:
        raise ConstantsError(f"Error comparing constants: {e}") from e


def get_constant_info() -> Dict[str, Any]:
    """Get information about the constants database."""
    try:
        categories = {}
        for name, info in ALL_CONSTANTS.items():
            category = info["category"]
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return {
            "total_constants": len(ALL_CONSTANTS),
            "categories": categories,
            "precision_note": "High precision values available with precision='high' parameter",
            "sources": {
                "mathematical": "Standard mathematical references",
                "physical": "CODATA 2018 recommended values",
                "astronomical": "IAU and standard astronomical references"
            },
            "operation": "get_constant_info"
        }
        
    except Exception as e:
        raise ConstantsError(f"Error getting constant info: {e}") from e