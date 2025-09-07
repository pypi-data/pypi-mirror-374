"""
Unit conversion system for the Scientific Calculator MCP Server.

This module provides comprehensive unit conversion capabilities across
multiple unit types including length, weight, temperature, volume, time,
energy, pressure, and other scientific units.
"""

from typing import Dict, Any, List, Union, Optional
from decimal import Decimal, getcontext
import math

from calculator.models.errors import CalculatorError, ValidationError


class UnitConversionError(CalculatorError):
    """Error for unit conversion operations."""
    pass


# Unit conversion database with base unit conversions
# All conversions are to/from the base unit for each category

UNIT_DATABASE = {
    "length": {
        "base_unit": "meter",
        "units": {
            # Metric units
            "meter": 1.0,
            "m": 1.0,
            "kilometer": 1000.0,
            "km": 1000.0,
            "centimeter": 0.01,
            "cm": 0.01,
            "millimeter": 0.001,
            "mm": 0.001,
            "micrometer": 1e-6,
            "μm": 1e-6,
            "nanometer": 1e-9,
            "nm": 1e-9,
            
            # Imperial units
            "inch": 0.0254,
            "in": 0.0254,
            "foot": 0.3048,
            "ft": 0.3048,
            "yard": 0.9144,
            "yd": 0.9144,
            "mile": 1609.344,
            "mi": 1609.344,
            
            # Nautical
            "nautical_mile": 1852.0,
            "nmi": 1852.0,
            
            # Other
            "angstrom": 1e-10,
            "Å": 1e-10,
            "light_year": 9.461e15,
            "ly": 9.461e15,
            "astronomical_unit": 1.496e11,
            "au": 1.496e11,
        }
    },
    
    "weight": {
        "base_unit": "kilogram",
        "units": {
            # Metric units
            "kilogram": 1.0,
            "kg": 1.0,
            "gram": 0.001,
            "g": 0.001,
            "milligram": 1e-6,
            "mg": 1e-6,
            "microgram": 1e-9,
            "μg": 1e-9,
            "tonne": 1000.0,
            "t": 1000.0,
            "metric_ton": 1000.0,
            
            # Imperial units
            "pound": 0.453592,
            "lb": 0.453592,
            "ounce": 0.0283495,
            "oz": 0.0283495,
            "stone": 6.35029,
            "st": 6.35029,
            "ton": 907.185,  # US ton
            "short_ton": 907.185,
            "long_ton": 1016.05,  # UK ton
            
            # Other
            "carat": 0.0002,
            "ct": 0.0002,
        }
    },
    
    "temperature": {
        "base_unit": "kelvin",
        "special_conversion": True,  # Temperature requires special handling
        "units": {
            "kelvin": "K",
            "k": "K",
            "celsius": "C",
            "c": "C",
            "fahrenheit": "F",
            "f": "F",
            "rankine": "R",
            "r": "R",
        }
    },
    
    "volume": {
        "base_unit": "cubic_meter",
        "units": {
            # Metric units
            "cubic_meter": 1.0,
            "m³": 1.0,
            "m3": 1.0,
            "liter": 0.001,
            "l": 0.001,
            "milliliter": 1e-6,
            "ml": 1e-6,
            "cubic_centimeter": 1e-6,
            "cm³": 1e-6,
            "cm3": 1e-6,
            "cubic_millimeter": 1e-9,
            "mm³": 1e-9,
            "mm3": 1e-9,
            
            # Imperial units
            "gallon": 0.00378541,  # US gallon
            "gal": 0.00378541,
            "us_gallon": 0.00378541,
            "imperial_gallon": 0.00454609,  # UK gallon
            "uk_gallon": 0.00454609,
            "quart": 0.000946353,  # US quart
            "qt": 0.000946353,
            "pint": 0.000473176,  # US pint
            "pt": 0.000473176,
            "cup": 0.000236588,  # US cup
            "fluid_ounce": 2.95735e-5,  # US fluid ounce
            "fl_oz": 2.95735e-5,
            "tablespoon": 1.47868e-5,  # US tablespoon
            "tbsp": 1.47868e-5,
            "teaspoon": 4.92892e-6,  # US teaspoon
            "tsp": 4.92892e-6,
            
            # Other
            "cubic_inch": 1.63871e-5,
            "in³": 1.63871e-5,
            "in3": 1.63871e-5,
            "cubic_foot": 0.0283168,
            "ft³": 0.0283168,
            "ft3": 0.0283168,
            "barrel": 0.158987,  # Oil barrel
            "bbl": 0.158987,
        }
    },
    
    "time": {
        "base_unit": "second",
        "units": {
            "second": 1.0,
            "s": 1.0,
            "millisecond": 0.001,
            "ms": 0.001,
            "microsecond": 1e-6,
            "μs": 1e-6,
            "nanosecond": 1e-9,
            "ns": 1e-9,
            "minute": 60.0,
            "min": 60.0,
            "hour": 3600.0,
            "h": 3600.0,
            "hr": 3600.0,
            "day": 86400.0,
            "d": 86400.0,
            "week": 604800.0,
            "wk": 604800.0,
            "month": 2629746.0,  # Average month (30.44 days)
            "year": 31556952.0,  # Average year (365.25 days)
            "yr": 31556952.0,
            "decade": 315569520.0,
            "century": 3155695200.0,
        }
    },
    
    "energy": {
        "base_unit": "joule",
        "units": {
            # SI units
            "joule": 1.0,
            "j": 1.0,
            "kilojoule": 1000.0,
            "kj": 1000.0,
            "megajoule": 1e6,
            "mj": 1e6,
            "gigajoule": 1e9,
            "gj": 1e9,
            
            # Other energy units
            "calorie": 4.184,  # Thermochemical calorie
            "cal": 4.184,
            "kilocalorie": 4184.0,
            "kcal": 4184.0,
            "btu": 1055.06,  # British thermal unit
            "watt_hour": 3600.0,
            "wh": 3600.0,
            "kilowatt_hour": 3.6e6,
            "kwh": 3.6e6,
            "electron_volt": 1.602176634e-19,
            "ev": 1.602176634e-19,
            "kiloelectron_volt": 1.602176634e-16,
            "kev": 1.602176634e-16,
            "megaelectron_volt": 1.602176634e-13,
            "mev": 1.602176634e-13,
            
            # Foot-pound
            "foot_pound": 1.35582,
            "ft_lb": 1.35582,
        }
    },
    
    "pressure": {
        "base_unit": "pascal",
        "units": {
            # SI units
            "pascal": 1.0,
            "pa": 1.0,
            "kilopascal": 1000.0,
            "kpa": 1000.0,
            "megapascal": 1e6,
            "mpa": 1e6,
            "gigapascal": 1e9,
            "gpa": 1e9,
            
            # Other pressure units
            "bar": 100000.0,
            "millibar": 100.0,
            "mbar": 100.0,
            "atmosphere": 101325.0,
            "atm": 101325.0,
            "torr": 133.322,
            "mmhg": 133.322,  # Millimeters of mercury
            "psi": 6894.76,  # Pounds per square inch
            "pounds_per_square_inch": 6894.76,
            "psf": 47.8803,  # Pounds per square foot
            "pounds_per_square_foot": 47.8803,
        }
    },
    
    "power": {
        "base_unit": "watt",
        "units": {
            "watt": 1.0,
            "w": 1.0,
            "kilowatt": 1000.0,
            "kw": 1000.0,
            "megawatt": 1e6,
            "mw": 1e6,
            "gigawatt": 1e9,
            "gw": 1e9,
            "horsepower": 745.7,  # Mechanical horsepower
            "hp": 745.7,
            "metric_horsepower": 735.5,
            "ps": 735.5,
            "btu_per_hour": 0.293071,
            "btu/h": 0.293071,
        }
    },
    
    "frequency": {
        "base_unit": "hertz",
        "units": {
            "hertz": 1.0,
            "hz": 1.0,
            "kilohertz": 1000.0,
            "khz": 1000.0,
            "megahertz": 1e6,
            "mhz": 1e6,
            "gigahertz": 1e9,
            "ghz": 1e9,
            "terahertz": 1e12,
            "thz": 1e12,
            "rpm": 1.0/60.0,  # Revolutions per minute
            "revolutions_per_minute": 1.0/60.0,
        }
    },
    
    "area": {
        "base_unit": "square_meter",
        "units": {
            # Metric units
            "square_meter": 1.0,
            "m²": 1.0,
            "m2": 1.0,
            "square_kilometer": 1e6,
            "km²": 1e6,
            "km2": 1e6,
            "square_centimeter": 1e-4,
            "cm²": 1e-4,
            "cm2": 1e-4,
            "square_millimeter": 1e-6,
            "mm²": 1e-6,
            "mm2": 1e-6,
            "hectare": 10000.0,
            "ha": 10000.0,
            
            # Imperial units
            "square_inch": 0.00064516,
            "in²": 0.00064516,
            "in2": 0.00064516,
            "square_foot": 0.092903,
            "ft²": 0.092903,
            "ft2": 0.092903,
            "square_yard": 0.836127,
            "yd²": 0.836127,
            "yd2": 0.836127,
            "square_mile": 2.59e6,
            "mi²": 2.59e6,
            "mi2": 2.59e6,
            "acre": 4046.86,
        }
    },
    
    "speed": {
        "base_unit": "meter_per_second",
        "units": {
            "meter_per_second": 1.0,
            "m/s": 1.0,
            "kilometer_per_hour": 0.277778,
            "km/h": 0.277778,
            "kmh": 0.277778,
            "mile_per_hour": 0.44704,
            "mph": 0.44704,
            "mi/h": 0.44704,
            "foot_per_second": 0.3048,
            "ft/s": 0.3048,
            "knot": 0.514444,
            "kt": 0.514444,
            "nautical_mile_per_hour": 0.514444,
        }
    }
}


def _validate_unit_type(unit_type: str) -> str:
    """Validate and normalize unit type."""
    if unit_type.lower() not in UNIT_DATABASE:
        available_types = ', '.join(sorted(UNIT_DATABASE.keys()))
        raise ValidationError(f"Unknown unit type: {unit_type}. Available types: {available_types}")
    return unit_type.lower()


def _validate_unit(unit: str, unit_type: str) -> str:
    """Validate and normalize unit name within a unit type."""
    unit_data = UNIT_DATABASE[unit_type]
    
    if unit.lower() not in unit_data["units"]:
        available_units = ', '.join(sorted(unit_data["units"].keys()))
        raise ValidationError(
            f"Unknown {unit_type} unit: {unit}. Available units: {available_units}"
        )
    return unit.lower()


def _validate_numeric_value(value: Union[float, int, str]) -> float:
    """Validate and convert numeric value."""
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Invalid numeric value: {value}") from e


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Special temperature conversion handling."""
    # Normalize unit names
    unit_map = {
        "kelvin": "K", "k": "K",
        "celsius": "C", "c": "C",
        "fahrenheit": "F", "f": "F",
        "rankine": "R", "r": "R"
    }
    
    from_unit = unit_map.get(from_unit.lower(), from_unit.upper())
    to_unit = unit_map.get(to_unit.lower(), to_unit.upper())
    
    # Convert to Kelvin first
    if from_unit == "K":
        kelvin_value = value
    elif from_unit == "C":
        kelvin_value = value + 273.15
    elif from_unit == "F":
        kelvin_value = (value - 32) * 5/9 + 273.15
    elif from_unit == "R":
        kelvin_value = value * 5/9
    else:
        raise ValidationError(f"Unknown temperature unit: {from_unit}")
    
    # Convert from Kelvin to target unit
    if to_unit == "K":
        result = kelvin_value
    elif to_unit == "C":
        result = kelvin_value - 273.15
    elif to_unit == "F":
        result = (kelvin_value - 273.15) * 9/5 + 32
    elif to_unit == "R":
        result = kelvin_value * 9/5
    else:
        raise ValidationError(f"Unknown temperature unit: {to_unit}")
    
    return result


def convert_units(value: Union[float, int, str], 
                 from_unit: str, 
                 to_unit: str, 
                 unit_type: str) -> Dict[str, Any]:
    """Convert a value from one unit to another within the same unit type."""
    try:
        # Validate inputs
        numeric_value = _validate_numeric_value(value)
        validated_unit_type = _validate_unit_type(unit_type)
        
        # Handle temperature conversion specially
        if validated_unit_type == "temperature":
            result_value = _convert_temperature(numeric_value, from_unit, to_unit)
            
            return {
                "result": result_value,
                "original_value": numeric_value,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "unit_type": unit_type,
                "conversion_method": "temperature_special",
                "operation": "unit_conversion"
            }
        
        # Validate units for non-temperature conversions
        validated_from_unit = _validate_unit(from_unit, validated_unit_type)
        validated_to_unit = _validate_unit(to_unit, validated_unit_type)
        
        # Get conversion factors
        unit_data = UNIT_DATABASE[validated_unit_type]
        from_factor = unit_data["units"][validated_from_unit]
        to_factor = unit_data["units"][validated_to_unit]
        
        # Convert: value * from_factor / to_factor
        # This converts to base unit first, then to target unit
        result_value = numeric_value * from_factor / to_factor
        
        # Calculate conversion factor for reference
        conversion_factor = from_factor / to_factor
        
        return {
            "result": result_value,
            "original_value": numeric_value,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "unit_type": unit_type,
            "conversion_factor": conversion_factor,
            "base_unit": unit_data["base_unit"],
            "operation": "unit_conversion"
        }
        
    except Exception as e:
        raise UnitConversionError(f"Error converting units: {e}") from e


def get_available_units(unit_type: str = None) -> Dict[str, Any]:
    """Get available units for a specific type or all types."""
    try:
        if unit_type is None:
            # Return all unit types and their units
            result = {}
            for utype, data in UNIT_DATABASE.items():
                result[utype] = {
                    "base_unit": data["base_unit"],
                    "units": list(data["units"].keys()) if "units" in data else list(data["units"].keys()),
                    "special_conversion": data.get("special_conversion", False)
                }
            return {
                "unit_types": result,
                "total_types": len(UNIT_DATABASE),
                "operation": "get_available_units"
            }
        else:
            # Return units for specific type
            validated_unit_type = _validate_unit_type(unit_type)
            unit_data = UNIT_DATABASE[validated_unit_type]
            
            return {
                "unit_type": unit_type,
                "base_unit": unit_data["base_unit"],
                "units": list(unit_data["units"].keys()) if "units" in unit_data else list(unit_data["units"].keys()),
                "unit_count": len(unit_data["units"]) if "units" in unit_data else len(unit_data["units"]),
                "special_conversion": unit_data.get("special_conversion", False),
                "operation": "get_available_units"
            }
            
    except Exception as e:
        raise UnitConversionError(f"Error getting available units: {e}") from e


def validate_unit_compatibility(from_unit: str, to_unit: str, unit_type: str) -> Dict[str, Any]:
    """Validate that two units are compatible for conversion."""
    try:
        validated_unit_type = _validate_unit_type(unit_type)
        
        # For temperature, use special validation
        if validated_unit_type == "temperature":
            temp_units = UNIT_DATABASE["temperature"]["units"]
            from_valid = from_unit.lower() in temp_units
            to_valid = to_unit.lower() in temp_units
            
            return {
                "compatible": from_valid and to_valid,
                "from_unit_valid": from_valid,
                "to_unit_valid": to_valid,
                "unit_type": unit_type,
                "special_conversion": True,
                "operation": "validate_unit_compatibility"
            }
        
        # For other unit types
        unit_data = UNIT_DATABASE[validated_unit_type]
        from_valid = from_unit.lower() in unit_data["units"]
        to_valid = to_unit.lower() in unit_data["units"]
        
        return {
            "compatible": from_valid and to_valid,
            "from_unit_valid": from_valid,
            "to_unit_valid": to_valid,
            "unit_type": unit_type,
            "base_unit": unit_data["base_unit"],
            "special_conversion": False,
            "operation": "validate_unit_compatibility"
        }
        
    except Exception as e:
        raise UnitConversionError(f"Error validating unit compatibility: {e}") from e


def get_conversion_factor(from_unit: str, to_unit: str, unit_type: str) -> Dict[str, Any]:
    """Get the conversion factor between two units."""
    try:
        validated_unit_type = _validate_unit_type(unit_type)
        
        # Temperature conversions don't have simple factors
        if validated_unit_type == "temperature":
            raise UnitConversionError(
                "Temperature conversions don't have simple multiplication factors. "
                "Use convert_units() for temperature conversions."
            )
        
        validated_from_unit = _validate_unit(from_unit, validated_unit_type)
        validated_to_unit = _validate_unit(to_unit, validated_unit_type)
        
        # Get conversion factors
        unit_data = UNIT_DATABASE[validated_unit_type]
        from_factor = unit_data["units"][validated_from_unit]
        to_factor = unit_data["units"][validated_to_unit]
        
        conversion_factor = from_factor / to_factor
        
        return {
            "conversion_factor": conversion_factor,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "unit_type": unit_type,
            "base_unit": unit_data["base_unit"],
            "from_to_base_factor": from_factor,
            "to_to_base_factor": to_factor,
            "operation": "get_conversion_factor"
        }
        
    except Exception as e:
        raise UnitConversionError(f"Error getting conversion factor: {e}") from e


def convert_multiple_units(value: Union[float, int, str], 
                          from_unit: str, 
                          to_units: List[str], 
                          unit_type: str) -> Dict[str, Any]:
    """Convert a value to multiple target units."""
    try:
        results = {}
        errors = {}
        
        for to_unit in to_units:
            try:
                conversion_result = convert_units(value, from_unit, to_unit, unit_type)
                results[to_unit] = conversion_result["result"]
            except Exception as e:
                errors[to_unit] = str(e)
        
        return {
            "results": results,
            "errors": errors,
            "original_value": _validate_numeric_value(value),
            "from_unit": from_unit,
            "unit_type": unit_type,
            "successful_conversions": len(results),
            "failed_conversions": len(errors),
            "operation": "convert_multiple_units"
        }
        
    except Exception as e:
        raise UnitConversionError(f"Error in multiple unit conversion: {e}") from e


def find_unit_by_name(unit_name: str) -> Dict[str, Any]:
    """Find which unit type(s) contain a specific unit name."""
    try:
        matches = {}
        
        for unit_type, data in UNIT_DATABASE.items():
            if "units" in data and unit_name.lower() in data["units"]:
                matches[unit_type] = {
                    "base_unit": data["base_unit"],
                    "conversion_factor": data["units"][unit_name.lower()],
                    "special_conversion": data.get("special_conversion", False)
                }
        
        return {
            "unit_name": unit_name,
            "matches": matches,
            "match_count": len(matches),
            "operation": "find_unit_by_name"
        }
        
    except Exception as e:
        raise UnitConversionError(f"Error finding unit: {e}") from e


def get_unit_info(unit_name: str, unit_type: str) -> Dict[str, Any]:
    """Get detailed information about a specific unit."""
    try:
        validated_unit_type = _validate_unit_type(unit_type)
        validated_unit = _validate_unit(unit_name, validated_unit_type)
        
        unit_data = UNIT_DATABASE[validated_unit_type]
        
        if validated_unit_type == "temperature":
            return {
                "unit_name": unit_name,
                "unit_type": unit_type,
                "base_unit": unit_data["base_unit"],
                "special_conversion": True,
                "description": "Temperature unit requiring special conversion formulas",
                "operation": "get_unit_info"
            }
        
        conversion_factor = unit_data["units"][validated_unit]
        
        return {
            "unit_name": unit_name,
            "unit_type": unit_type,
            "base_unit": unit_data["base_unit"],
            "conversion_factor_to_base": conversion_factor,
            "conversion_factor_from_base": 1.0 / conversion_factor,
            "special_conversion": False,
            "operation": "get_unit_info"
        }
        
    except Exception as e:
        raise UnitConversionError(f"Error getting unit info: {e}") from e