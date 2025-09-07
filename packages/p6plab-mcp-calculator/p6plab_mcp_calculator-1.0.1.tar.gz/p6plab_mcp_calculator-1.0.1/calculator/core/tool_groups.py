"""
Tool Group Management System

This module provides functionality to selectively enable/disable groups of mathematical tools
based on environment variables. It supports individual group controls, preset combinations,
and backward compatibility.
"""

import os
from typing import Dict, List, Set, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToolGroup(str, Enum):
    """Enumeration of available tool groups."""
    BASIC = "basic"
    ADVANCED = "advanced"
    STATISTICS = "statistics"
    MATRIX = "matrix"
    COMPLEX = "complex"
    UNITS = "units"
    CALCULUS = "calculus"
    SOLVER = "solver"
    FINANCIAL = "financial"
    CURRENCY = "currency"
    CONSTANTS = "constants"


class PresetCombination(str, Enum):
    """Enumeration of preset tool group combinations."""
    ALL = "all"
    SCIENTIFIC = "scientific"
    BUSINESS = "business"
    ENGINEERING = "engineering"


class ToolGroupRegistry:
    """Registry that maintains mapping between tool groups and individual tools."""
    
    # Complete mapping of tool groups to their respective tools
    TOOL_GROUPS: Dict[str, Dict[str, Any]] = {
        ToolGroup.BASIC: {
            'tools': [
                'health_check', 'add', 'subtract', 'multiply', 
                'divide', 'power', 'square_root', 'calculate'
            ],
            'description': 'Basic arithmetic operations',
            'default_enabled': True
        },
        ToolGroup.ADVANCED: {
            'tools': [
                'trigonometric', 'logarithm', 'exponential', 
                'hyperbolic', 'convert_angle'
            ],
            'description': 'Advanced mathematical functions',
            'default_enabled': False
        },
        ToolGroup.STATISTICS: {
            'tools': [
                'descriptive_stats', 'probability_distribution', 
                'correlation_analysis', 'regression_analysis', 'hypothesis_test'
            ],
            'description': 'Statistical analysis tools',
            'default_enabled': False
        },
        ToolGroup.MATRIX: {
            'tools': [
                'matrix_multiply', 'matrix_determinant', 'matrix_inverse', 
                'matrix_eigenvalues', 'solve_linear_system', 'matrix_operations',
                'matrix_arithmetic', 'create_matrix'
            ],
            'description': 'Matrix operations and linear algebra',
            'default_enabled': False
        },
        ToolGroup.COMPLEX: {
            'tools': [
                'complex_arithmetic', 'complex_magnitude', 'complex_phase',
                'complex_conjugate', 'polar_conversion', 'complex_functions'
            ],
            'description': 'Complex number operations',
            'default_enabled': False
        },
        ToolGroup.UNITS: {
            'tools': [
                'convert_units', 'get_available_units', 'validate_unit_compatibility',
                'get_conversion_factor', 'convert_multiple_units', 
                'find_unit_by_name', 'get_unit_info'
            ],
            'description': 'Unit conversion tools',
            'default_enabled': False
        },
        ToolGroup.CALCULUS: {
            'tools': [
                'derivative', 'integral', 'numerical_derivative', 
                'numerical_integral', 'calculate_limit', 'taylor_series',
                'find_critical_points', 'gradient', 'evaluate_expression'
            ],
            'description': 'Calculus operations (symbolic and numerical)',
            'default_enabled': False
        },
        ToolGroup.SOLVER: {
            'tools': [
                'solve_linear', 'solve_quadratic', 'solve_polynomial',
                'solve_system', 'find_roots', 'analyze_equation'
            ],
            'description': 'Equation solving tools',
            'default_enabled': False
        },
        ToolGroup.FINANCIAL: {
            'tools': [
                'compound_interest', 'loan_payment', 'net_present_value',
                'internal_rate_of_return', 'present_value', 
                'future_value_annuity', 'amortization_schedule'
            ],
            'description': 'Financial mathematics tools',
            'default_enabled': False
        },
        ToolGroup.CURRENCY: {
            'tools': [
                'convert_currency', 'get_exchange_rate', 
                'get_supported_currencies', 'get_currency_info'
            ],
            'description': 'Currency conversion tools',
            'default_enabled': False
        },
        ToolGroup.CONSTANTS: {
            'tools': [
                'get_constant', 'list_constants', 'search_constants'
            ],
            'description': 'Mathematical and physical constants',
            'default_enabled': False
        }
    }
    
    # Preset combinations mapping
    PRESET_COMBINATIONS: Dict[str, List[str]] = {
        PresetCombination.ALL: list(TOOL_GROUPS.keys()),
        PresetCombination.SCIENTIFIC: [
            ToolGroup.BASIC, ToolGroup.ADVANCED, ToolGroup.STATISTICS,
            ToolGroup.MATRIX, ToolGroup.COMPLEX, ToolGroup.CALCULUS
        ],
        PresetCombination.BUSINESS: [
            ToolGroup.BASIC, ToolGroup.FINANCIAL, 
            ToolGroup.CURRENCY, ToolGroup.UNITS
        ],
        PresetCombination.ENGINEERING: [
            ToolGroup.BASIC, ToolGroup.ADVANCED, ToolGroup.MATRIX,
            ToolGroup.COMPLEX, ToolGroup.CALCULUS, ToolGroup.UNITS, ToolGroup.CONSTANTS
        ]
    }
    
    def __init__(self):
        """Initialize the tool group registry."""
        self._tool_to_group_map = self._build_tool_to_group_map()
    
    def _build_tool_to_group_map(self) -> Dict[str, str]:
        """Build reverse mapping from tool names to their groups."""
        tool_to_group = {}
        for group_name, group_info in self.TOOL_GROUPS.items():
            for tool_name in group_info['tools']:
                tool_to_group[tool_name] = group_name
        return tool_to_group
    
    def get_tools_for_group(self, group_name: str) -> List[str]:
        """Get all tools belonging to a specific group."""
        if group_name not in self.TOOL_GROUPS:
            return []
        return self.TOOL_GROUPS[group_name]['tools'].copy()
    
    def get_group_for_tool(self, tool_name: str) -> Optional[str]:
        """Get the group name for a specific tool."""
        return self._tool_to_group_map.get(tool_name)
    
    def get_all_groups(self) -> List[str]:
        """Get list of all available tool groups."""
        return list(self.TOOL_GROUPS.keys())
    
    def get_group_description(self, group_name: str) -> str:
        """Get description for a tool group."""
        if group_name not in self.TOOL_GROUPS:
            return ""
        return self.TOOL_GROUPS[group_name]['description']
    
    def is_default_enabled(self, group_name: str) -> bool:
        """Check if a group is enabled by default."""
        if group_name not in self.TOOL_GROUPS:
            return False
        return self.TOOL_GROUPS[group_name]['default_enabled']
    
    def get_preset_groups(self, preset_name: str) -> List[str]:
        """Get tool groups for a preset combination."""
        return self.PRESET_COMBINATIONS.get(preset_name, [])
    
    def get_all_presets(self) -> List[str]:
        """Get list of all available preset combinations."""
        return list(self.PRESET_COMBINATIONS.keys())
    
    def get_preset_info(self, preset_name: str) -> Dict[str, Any]:
        """Get detailed information about a preset combination."""
        if preset_name not in self.PRESET_COMBINATIONS:
            return {}
        
        groups = self.PRESET_COMBINATIONS[preset_name]
        total_tools = sum(len(self.TOOL_GROUPS[group]['tools']) for group in groups)
        
        return {
            "name": preset_name,
            "groups": groups,
            "group_count": len(groups),
            "total_tools": total_tools,
            "descriptions": {
                group: self.TOOL_GROUPS[group]['description'] 
                for group in groups
            }
        }
    
    def get_all_preset_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed information about all preset combinations."""
        return {
            preset: self.get_preset_info(preset) 
            for preset in self.get_all_presets()
        }
    
    def get_total_tool_count(self) -> int:
        """Get total number of tools across all groups."""
        total = 0
        for group_info in self.TOOL_GROUPS.values():
            total += len(group_info['tools'])
        return total


class ToolGroupConfig:
    """Configuration manager for tool groups based on environment variables."""
    
    def __init__(self, registry: Optional[ToolGroupRegistry] = None):
        """Initialize configuration manager."""
        self.registry = registry or ToolGroupRegistry()
        self.enabled_groups: Set[str] = set()
        self.warnings: List[str] = []
        self.configuration_source: str = "default"
        
    def load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        self.enabled_groups.clear()
        self.warnings.clear()
        
        # Check for preset combinations first (they take precedence)
        preset_found = self._load_preset_combinations()
        
        # If no presets found, check individual group settings
        if not preset_found:
            self._load_individual_groups()
        
        # Check legacy support
        self._check_legacy_variables()
        
        # Basic group is always enabled
        self.enabled_groups.add(ToolGroup.BASIC)
        
        # Set default configuration source if only basic is enabled
        if len(self.enabled_groups) == 1 and ToolGroup.BASIC in self.enabled_groups:
            self.configuration_source = "default"
            logger.info("Using default configuration: basic arithmetic tools only")
        
        # Validate that we have at least some tools enabled
        self._validate_configuration()
        
        # Log final configuration
        self._log_configuration()
    
    def _load_preset_combinations(self) -> bool:
        """Load preset combinations from environment variables."""
        preset_found = False
        active_presets = []
        
        # Check CALCULATOR_ENABLE_ALL first (highest precedence)
        if self._get_bool_env("CALCULATOR_ENABLE_ALL"):
            preset_groups = self.registry.get_preset_groups(PresetCombination.ALL)
            self.enabled_groups.update(preset_groups)
            self.configuration_source = "preset_all"
            preset_found = True
            active_presets.append("ALL")
            logger.info(f"Enabled all {len(preset_groups)} tool groups via CALCULATOR_ENABLE_ALL")
        
        # Check other presets (can be combined)
        presets = [
            (PresetCombination.SCIENTIFIC, "CALCULATOR_ENABLE_SCIENTIFIC"),
            (PresetCombination.BUSINESS, "CALCULATOR_ENABLE_BUSINESS"),
            (PresetCombination.ENGINEERING, "CALCULATOR_ENABLE_ENGINEERING")
        ]
        
        for preset_name, env_var in presets:
            if self._get_bool_env(env_var):
                preset_groups = self.registry.get_preset_groups(preset_name)
                self.enabled_groups.update(preset_groups)
                preset_found = True
                active_presets.append(preset_name.upper())
                
                logger.info(f"Enabled {preset_name} preset ({len(preset_groups)} groups) via {env_var}")
                logger.debug(f"  {preset_name} groups: {preset_groups}")
        
        # Update configuration source for multiple presets
        if len(active_presets) > 1:
            self.configuration_source = f"preset_combined_{'+'.join(active_presets)}"
        elif len(active_presets) == 1 and active_presets[0] != "ALL":
            self.configuration_source = f"preset_{active_presets[0].lower()}"
        
        if preset_found:
            logger.info(f"Preset configuration complete: {len(self.enabled_groups)} groups enabled")
        
        return preset_found
    
    def _load_individual_groups(self) -> None:
        """Load individual group settings from environment variables."""
        individual_groups_found = False
        
        for group_name in self.registry.get_all_groups():
            # Skip basic group - it's always enabled
            if group_name == ToolGroup.BASIC:
                continue
                
            env_var = f"CALCULATOR_ENABLE_{group_name.upper()}"
            if self._get_bool_env(env_var):
                self.enabled_groups.add(group_name)
                individual_groups_found = True
                logger.info(f"Enabled {group_name} group via {env_var}")
        
        if individual_groups_found:
            self.configuration_source = "individual"
    
    def _check_legacy_variables(self) -> None:
        """Check for legacy environment variables and provide compatibility."""
        legacy_vars = {
            "CALCULATOR_ENABLE_ALL_TOOLS": "CALCULATOR_ENABLE_ALL"
        }
        
        for legacy_var, modern_var in legacy_vars.items():
            if self._get_bool_env(legacy_var):
                if not self.enabled_groups:
                    # No modern configuration found, use legacy
                    self.enabled_groups.update(self.registry.get_preset_groups(PresetCombination.ALL))
                    self.configuration_source = "legacy"
                    
                    warning_msg = (
                        f"Using legacy {legacy_var} variable. "
                        f"Consider migrating to {modern_var} for future compatibility."
                    )
                    logger.warning(warning_msg)
                    
                    migration_msg = (
                        f"Legacy environment variable {legacy_var} is deprecated. "
                        f"Use {modern_var} instead. "
                        f"Migration: Change {legacy_var}=true to {modern_var}=true"
                    )
                    self.warnings.append(migration_msg)
                    
                    logger.info(f"Legacy configuration enabled all {len(self.enabled_groups)} tool groups")
                else:
                    # Modern configuration takes precedence
                    precedence_msg = (
                        f"Legacy {legacy_var} ignored due to newer configuration. "
                        f"Remove {legacy_var} to avoid confusion."
                    )
                    logger.info(precedence_msg)
                    self.warnings.append(precedence_msg)
    
    def _get_bool_env(self, env_var: str) -> bool:
        """Get boolean value from environment variable with comprehensive validation."""
        raw_value = os.getenv(env_var, "")
        value = raw_value.lower().strip()
        
        # Handle empty values
        if not value:
            return False
        
        # Handle true values
        if value in ("true", "1", "yes", "on", "enable", "enabled"):
            logger.debug(f"{env_var}={raw_value} -> True")
            return True
        
        # Handle false values
        elif value in ("false", "0", "no", "off", "disable", "disabled"):
            logger.debug(f"{env_var}={raw_value} -> False")
            return False
        
        # Handle invalid values
        else:
            warning_msg = f"Invalid value '{raw_value}' for {env_var}, treating as false. Valid values: true/false, 1/0, yes/no, on/off"
            self.warnings.append(warning_msg)
            logger.warning(warning_msg)
            return False
    
    def _log_configuration(self) -> None:
        """Log the final configuration state."""
        enabled_count = sum(
            len(self.registry.get_tools_for_group(group)) 
            for group in self.enabled_groups
        )
        
        logger.info(f"Tool group configuration loaded:")
        logger.info(f"  Source: {self.configuration_source}")
        logger.info(f"  Enabled groups: {sorted(self.enabled_groups)}")
        logger.info(f"  Total enabled tools: {enabled_count}")
        
        if self.warnings:
            logger.warning(f"Configuration warnings: {self.warnings}")
    
    def is_group_enabled(self, group_name: str) -> bool:
        """Check if a specific group is enabled."""
        return group_name in self.enabled_groups
    
    def get_enabled_tools(self) -> List[str]:
        """Get list of all enabled tools."""
        enabled_tools = []
        for group_name in self.enabled_groups:
            enabled_tools.extend(self.registry.get_tools_for_group(group_name))
        return enabled_tools
    
    def get_group_status(self) -> Dict[str, bool]:
        """Get status of all tool groups."""
        return {
            group_name: self.is_group_enabled(group_name)
            for group_name in self.registry.get_all_groups()
        }
    
    def get_enabled_groups(self) -> Set[str]:
        """Get set of enabled group names."""
        return self.enabled_groups.copy()
    
    def get_disabled_groups(self) -> Set[str]:
        """Get set of disabled group names."""
        all_groups = set(self.registry.get_all_groups())
        return all_groups - self.enabled_groups
    
    def validate_environment_variables(self) -> Dict[str, Any]:
        """Validate all tool group environment variables and return validation report."""
        validation_report = {
            "valid_variables": [],
            "invalid_variables": [],
            "unused_variables": [],
            "recommendations": []
        }
        
        # Check all possible tool group environment variables
        all_env_vars = []
        
        # Individual group variables
        for group_name in self.registry.get_all_groups():
            env_var = f"CALCULATOR_ENABLE_{group_name.upper()}"
            all_env_vars.append(env_var)
        
        # Preset variables
        preset_vars = [
            "CALCULATOR_ENABLE_ALL",
            "CALCULATOR_ENABLE_SCIENTIFIC", 
            "CALCULATOR_ENABLE_BUSINESS",
            "CALCULATOR_ENABLE_ENGINEERING"
        ]
        all_env_vars.extend(preset_vars)
        
        # Legacy variables
        legacy_vars = ["CALCULATOR_ENABLE_ALL_TOOLS"]
        all_env_vars.extend(legacy_vars)
        
        # Validate each variable
        for env_var in all_env_vars:
            raw_value = os.getenv(env_var)
            if raw_value is not None:
                # Variable is set, validate its value
                try:
                    parsed_value = self._get_bool_env(env_var)
                    validation_report["valid_variables"].append({
                        "name": env_var,
                        "raw_value": raw_value,
                        "parsed_value": parsed_value
                    })
                except Exception as e:
                    validation_report["invalid_variables"].append({
                        "name": env_var,
                        "raw_value": raw_value,
                        "error": str(e)
                    })
        
        # Add recommendations
        if not validation_report["valid_variables"]:
            validation_report["recommendations"].append(
                "No tool group environment variables set. Only basic arithmetic tools will be available."
            )
        
        if len(self.enabled_groups) == len(self.registry.get_all_groups()):
            validation_report["recommendations"].append(
                "All tool groups are enabled. Consider using CALCULATOR_ENABLE_ALL=true for clarity."
            )
        
        return validation_report
    
    def _validate_configuration(self) -> None:
        """Validate the current configuration and ensure it's usable."""
        if not self.enabled_groups:
            # This should never happen due to default fallback, but let's be safe
            self.enabled_groups.add(ToolGroup.BASIC)
            self.warnings.append("Configuration validation: No groups enabled, forced basic group activation")
            logger.warning("Configuration validation forced basic group activation")
        
        # Check if basic group is available (it should always be)
        if ToolGroup.BASIC not in self.enabled_groups:
            # If basic is not enabled, we should warn about potential usability issues
            self.warnings.append(
                "Basic arithmetic tools are not enabled. "
                "Consider enabling CALCULATOR_ENABLE_BASIC=true for core functionality."
            )
        
        # Validate that all enabled groups actually exist
        invalid_groups = []
        for group in self.enabled_groups.copy():
            if group not in self.registry.get_all_groups():
                invalid_groups.append(group)
                self.enabled_groups.remove(group)
        
        if invalid_groups:
            warning_msg = f"Removed invalid tool groups: {invalid_groups}"
            self.warnings.append(warning_msg)
            logger.warning(warning_msg)
        
        # Log final validation results
        total_tools = len(self.get_enabled_tools())
        logger.info(f"Configuration validation complete: {len(self.enabled_groups)} groups, {total_tools} tools")
    
    def get_migration_recommendations(self) -> List[str]:
        """Get recommendations for migrating from legacy configuration."""
        recommendations = []
        
        # Check for legacy variables
        if os.getenv("CALCULATOR_ENABLE_ALL_TOOLS"):
            recommendations.append(
                "Replace CALCULATOR_ENABLE_ALL_TOOLS=true with CALCULATOR_ENABLE_ALL=true"
            )
        
        # Check for inefficient configurations
        if len(self.enabled_groups) == len(self.registry.get_all_groups()):
            if self.configuration_source.startswith("individual"):
                recommendations.append(
                    "You have enabled all groups individually. "
                    "Consider using CALCULATOR_ENABLE_ALL=true for simplicity."
                )
        
        # Check for redundant preset combinations
        if "preset_combined" in self.configuration_source:
            recommendations.append(
                "Multiple presets are enabled. "
                "Consider using CALCULATOR_ENABLE_ALL=true if you need all functionality."
            )
        
        return recommendations
    
    def reset_to_default(self) -> None:
        """Reset configuration to default state (basic tools only)."""
        self.enabled_groups.clear()
        self.enabled_groups.add(ToolGroup.BASIC)
        self.warnings.clear()
        self.configuration_source = "default"
        logger.info("Configuration reset to default (basic tools only)")
    
    def is_minimal_configuration(self) -> bool:
        """Check if current configuration is minimal (basic tools only)."""
        return self.enabled_groups == {ToolGroup.BASIC}
    
    def get_configuration_info(self) -> Dict[str, Any]:
        """Get comprehensive configuration information."""
        enabled_tools = self.get_enabled_tools()
        tool_counts_by_group = {
            group: len(self.registry.get_tools_for_group(group))
            for group in self.enabled_groups
        }
        
        return {
            "enabled_groups": sorted(self.enabled_groups),
            "disabled_groups": sorted(self.get_disabled_groups()),
            "total_enabled_tools": len(enabled_tools),
            "total_available_tools": self.registry.get_total_tool_count(),
            "tool_counts_by_group": tool_counts_by_group,
            "configuration_source": self.configuration_source,
            "warnings": self.warnings.copy(),
            "migration_recommendations": self.get_migration_recommendations()
        }