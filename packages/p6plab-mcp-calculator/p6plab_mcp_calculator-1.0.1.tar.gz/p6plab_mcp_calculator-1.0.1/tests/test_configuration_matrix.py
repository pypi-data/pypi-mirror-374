"""Configuration test matrix for tool group management.

This module provides comprehensive testing of all possible configuration
combinations and edge cases for the tool group management system.
"""

import os
import pytest
from unittest.mock import patch
from typing import Dict, List, Set, Any

from calculator.core.tool_filter import create_tool_filter_from_environment
from calculator.core.tool_groups import ToolGroup, PresetCombination


class ConfigurationTestMatrix:
    """Test matrix for all configuration combinations."""
    
    # Individual group configurations
    INDIVIDUAL_GROUP_CONFIGS = {
        "basic_only": {},  # Basic tools are always enabled
        "advanced_only": {"CALCULATOR_ENABLE_ADVANCED": "true"},
        "statistics_only": {"CALCULATOR_ENABLE_STATISTICS": "true"},
        "matrix_only": {"CALCULATOR_ENABLE_MATRIX": "true"},
        "complex_only": {"CALCULATOR_ENABLE_COMPLEX": "true"},
        "units_only": {"CALCULATOR_ENABLE_UNITS": "true"},
        "calculus_only": {"CALCULATOR_ENABLE_CALCULUS": "true"},
        "solver_only": {"CALCULATOR_ENABLE_SOLVER": "true"},
        "financial_only": {"CALCULATOR_ENABLE_FINANCIAL": "true"},
        "currency_only": {"CALCULATOR_ENABLE_CURRENCY": "true"},
        "constants_only": {"CALCULATOR_ENABLE_CONSTANTS": "true"},
    }
    
    # Preset configurations
    PRESET_CONFIGS = {
        "preset_all": {"CALCULATOR_ENABLE_ALL": "true"},
        "preset_scientific": {"CALCULATOR_ENABLE_SCIENTIFIC": "true"},
        "preset_business": {"CALCULATOR_ENABLE_BUSINESS": "true"},
        "preset_engineering": {"CALCULATOR_ENABLE_ENGINEERING": "true"},
    }
    
    # Combined configurations
    COMBINED_CONFIGS = {
        "basic_advanced": {
            "CALCULATOR_ENABLE_ADVANCED": "true"
        },
        "math_focused": {
            "CALCULATOR_ENABLE_ADVANCED": "true",
            "CALCULATOR_ENABLE_CALCULUS": "true",
            "CALCULATOR_ENABLE_MATRIX": "true"
        },
        "business_focused": {
            "CALCULATOR_ENABLE_FINANCIAL": "true",
            "CALCULATOR_ENABLE_CURRENCY": "true",
            "CALCULATOR_ENABLE_UNITS": "true"
        },
        "data_science": {
            "CALCULATOR_ENABLE_STATISTICS": "true",
            "CALCULATOR_ENABLE_MATRIX": "true",
            "CALCULATOR_ENABLE_CALCULUS": "true"
        },
    }
    
    # Legacy configurations
    LEGACY_CONFIGS = {
        "legacy_all": {"CALCULATOR_ENABLE_ALL_TOOLS": "true"},
        "legacy_with_new": {
            "CALCULATOR_ENABLE_ALL_TOOLS": "true",
            "CALCULATOR_ENABLE_ADVANCED": "true"  # New should take precedence
        },
    }
    
    # Multiple preset configurations
    MULTIPLE_PRESET_CONFIGS = {
        "scientific_business": {
            "CALCULATOR_ENABLE_SCIENTIFIC": "true",
            "CALCULATOR_ENABLE_BUSINESS": "true"
        },
        "scientific_engineering": {
            "CALCULATOR_ENABLE_SCIENTIFIC": "true",
            "CALCULATOR_ENABLE_ENGINEERING": "true"
        },
        "all_presets": {
            "CALCULATOR_ENABLE_SCIENTIFIC": "true",
            "CALCULATOR_ENABLE_BUSINESS": "true",
            "CALCULATOR_ENABLE_ENGINEERING": "true"
        },
    }
    
    # Edge case configurations
    EDGE_CASE_CONFIGS = {
        "empty_config": {},
        "all_false": {
            "CALCULATOR_ENABLE_ADVANCED": "false",
            "CALCULATOR_ENABLE_STATISTICS": "false",
            "CALCULATOR_ENABLE_MATRIX": "false"
        },
        "mixed_values": {
            "CALCULATOR_ENABLE_ADVANCED": "false",
            "CALCULATOR_ENABLE_STATISTICS": "1",
            "CALCULATOR_ENABLE_MATRIX": "0"
        },
        "invalid_values": {
            "CALCULATOR_ENABLE_ADVANCED": "maybe",
            "CALCULATOR_ENABLE_STATISTICS": "true",
            "CALCULATOR_ENABLE_MATRIX": "invalid"
        },
    }
    
    # Boolean value variations
    BOOLEAN_VALUE_CONFIGS = {
        "true_variations": {
            "CALCULATOR_ENABLE_ADVANCED": "TRUE",
            "CALCULATOR_ENABLE_STATISTICS": "True",
            "CALCULATOR_ENABLE_MATRIX": "1",
            "CALCULATOR_ENABLE_COMPLEX": "yes",
            "CALCULATOR_ENABLE_UNITS": "YES",
            "CALCULATOR_ENABLE_CALCULUS": "on",
            "CALCULATOR_ENABLE_SOLVER": "ON",
            "CALCULATOR_ENABLE_FINANCIAL": "enable",
            "CALCULATOR_ENABLE_CURRENCY": "enabled"
        },
        "false_variations": {
            "CALCULATOR_ENABLE_ADVANCED": "FALSE",
            "CALCULATOR_ENABLE_STATISTICS": "False",
            "CALCULATOR_ENABLE_MATRIX": "0",
            "CALCULATOR_ENABLE_COMPLEX": "no",
            "CALCULATOR_ENABLE_UNITS": "NO",
            "CALCULATOR_ENABLE_CALCULUS": "off",
            "CALCULATOR_ENABLE_SOLVER": "OFF",
            "CALCULATOR_ENABLE_FINANCIAL": "disable",
            "CALCULATOR_ENABLE_CURRENCY": "disabled",
            "CALCULATOR_ENABLE_CONSTANTS": ""
        },
    }
    
    @classmethod
    def get_all_configurations(cls) -> Dict[str, Dict[str, str]]:
        """Get all test configurations."""
        all_configs = {}
        all_configs.update(cls.INDIVIDUAL_GROUP_CONFIGS)
        all_configs.update(cls.PRESET_CONFIGS)
        all_configs.update(cls.COMBINED_CONFIGS)
        all_configs.update(cls.LEGACY_CONFIGS)
        all_configs.update(cls.MULTIPLE_PRESET_CONFIGS)
        all_configs.update(cls.EDGE_CASE_CONFIGS)
        all_configs.update(cls.BOOLEAN_VALUE_CONFIGS)
        return all_configs


class TestIndividualGroupConfigurations:
    """Test individual group configurations."""
    
    @pytest.mark.parametrize("config_name,env_vars", 
                           ConfigurationTestMatrix.INDIVIDUAL_GROUP_CONFIGS.items())
    def test_individual_group_configuration(self, config_name: str, env_vars: Dict[str, str]):
        """Test each individual group configuration."""
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Basic tools are always enabled
            assert "basic" in config_info["enabled_groups"]
            
            if config_name == "basic_only":
                # Only basic should be enabled (default configuration)
                assert len(config_info["enabled_groups"]) == 1
                assert config_info["configuration_source"] == "default"
            else:
                # Should have basic plus the specified group
                expected_groups = {"basic", config_name.replace("_only", "")}
                assert set(config_info["enabled_groups"]) == expected_groups
                assert config_info["configuration_source"] == "individual"
    
    def test_basic_group_tools(self):
        """Test basic group tools are always enabled."""
        # Test with no environment variables (default)
        with patch.dict(os.environ, {}, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            expected_basic_tools = [
                "health_check", "add", "subtract", "multiply", 
                "divide", "power", "square_root", "calculate"
            ]
            
            for tool in expected_basic_tools:
                assert filter_obj.is_tool_enabled(tool), f"Basic tool {tool} should always be enabled"
            
            # Non-basic tools should be disabled by default
            assert not filter_obj.is_tool_enabled("trigonometric")
            assert not filter_obj.is_tool_enabled("matrix_multiply")
    
    def test_advanced_group_tools(self):
        """Test advanced group tools are correctly identified."""
        env_vars = {"CALCULATOR_ENABLE_ADVANCED": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            expected_advanced_tools = [
                "trigonometric", "logarithm", "exponential", 
                "hyperbolic", "convert_angle"
            ]
            
            for tool in expected_advanced_tools:
                assert filter_obj.is_tool_enabled(tool), f"Advanced tool {tool} should be enabled"
            
            # Basic tools should also be enabled (default)
            assert filter_obj.is_tool_enabled("add")
            
            # Other groups should be disabled
            assert not filter_obj.is_tool_enabled("matrix_multiply")
            assert not filter_obj.is_tool_enabled("descriptive_stats")


class TestPresetConfigurations:
    """Test preset configurations."""
    
    @pytest.mark.parametrize("config_name,env_vars", 
                           ConfigurationTestMatrix.PRESET_CONFIGS.items())
    def test_preset_configuration(self, config_name: str, env_vars: Dict[str, str]):
        """Test each preset configuration."""
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Verify configuration source
            expected_source = config_name.replace("preset_", "preset_")
            assert config_info["configuration_source"] == expected_source
            
            # Verify expected groups are enabled
            if config_name == "preset_all":
                assert len(config_info["enabled_groups"]) == 11  # All groups
                assert config_info["total_enabled_tools"] == 68
            elif config_name == "preset_scientific":
                expected_groups = {"basic", "advanced", "statistics", "matrix", "complex", "calculus"}
                assert set(config_info["enabled_groups"]) == expected_groups
            elif config_name == "preset_business":
                expected_groups = {"basic", "financial", "currency", "units"}
                assert set(config_info["enabled_groups"]) == expected_groups
            elif config_name == "preset_engineering":
                expected_groups = {"basic", "advanced", "matrix", "complex", "calculus", "units", "constants"}
                assert set(config_info["enabled_groups"]) == expected_groups
    
    def test_scientific_preset_tools(self):
        """Test scientific preset includes correct tools."""
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Should include scientific tools
            scientific_tools = [
                "add",                  # basic
                "trigonometric",        # advanced
                "descriptive_stats",    # statistics
                "matrix_multiply",      # matrix
                "complex_arithmetic",   # complex
                "derivative"            # calculus
            ]
            
            for tool in scientific_tools:
                assert filter_obj.is_tool_enabled(tool), f"Scientific tool {tool} should be enabled"
            
            # Should not include business tools
            business_tools = ["compound_interest", "convert_currency"]
            for tool in business_tools:
                assert not filter_obj.is_tool_enabled(tool), f"Business tool {tool} should be disabled"
    
    def test_business_preset_tools(self):
        """Test business preset includes correct tools."""
        env_vars = {"CALCULATOR_ENABLE_BUSINESS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Should include business tools
            business_tools = [
                "add",                  # basic
                "compound_interest",    # financial
                "convert_currency",     # currency
                "convert_units"         # units
            ]
            
            for tool in business_tools:
                assert filter_obj.is_tool_enabled(tool), f"Business tool {tool} should be enabled"
            
            # Should not include scientific tools
            scientific_tools = ["derivative", "matrix_multiply"]
            for tool in scientific_tools:
                assert not filter_obj.is_tool_enabled(tool), f"Scientific tool {tool} should be disabled"


class TestCombinedConfigurations:
    """Test combined configurations."""
    
    @pytest.mark.parametrize("config_name,env_vars", 
                           ConfigurationTestMatrix.COMBINED_CONFIGS.items())
    def test_combined_configuration(self, config_name: str, env_vars: Dict[str, str]):
        """Test each combined configuration."""
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Should have multiple groups enabled
            assert len(config_info["enabled_groups"]) > 1
            assert config_info["configuration_source"] == "individual"
            
            # Verify all specified groups are enabled
            for env_var, value in env_vars.items():
                if value.lower() == "true":
                    group_name = env_var.replace("CALCULATOR_ENABLE_", "").lower()
                    assert group_name in config_info["enabled_groups"]
    
    def test_math_focused_configuration(self):
        """Test math-focused configuration."""
        env_vars = {
            "CALCULATOR_ENABLE_ADVANCED": "true",
            "CALCULATOR_ENABLE_CALCULUS": "true",
            "CALCULATOR_ENABLE_MATRIX": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Should have math tools
            math_tools = [
                "add", "trigonometric", "derivative", "matrix_multiply"
            ]
            
            for tool in math_tools:
                assert filter_obj.is_tool_enabled(tool)
            
            # Should not have business tools
            assert not filter_obj.is_tool_enabled("compound_interest")
            assert not filter_obj.is_tool_enabled("convert_currency")


class TestLegacyConfigurations:
    """Test legacy configurations."""
    
    @pytest.mark.parametrize("config_name,env_vars", 
                           ConfigurationTestMatrix.LEGACY_CONFIGS.items())
    def test_legacy_configuration(self, config_name: str, env_vars: Dict[str, str]):
        """Test each legacy configuration."""
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Should have warnings about legacy usage
            if "CALCULATOR_ENABLE_ALL_TOOLS" in env_vars:
                if config_name == "legacy_all":
                    assert config_info["configuration_source"] == "legacy"
                    assert len(config_info["warnings"]) > 0
                    assert any("deprecated" in warning.lower() for warning in config_info["warnings"])
                elif config_name == "legacy_with_new":
                    # New variables should take precedence
                    assert config_info["configuration_source"] == "individual"
                    assert "basic" in config_info["enabled_groups"]
                    assert len(config_info["enabled_groups"]) == 1  # Only basic
    
    def test_legacy_precedence(self):
        """Test legacy variable precedence rules."""
        # Legacy alone should enable all tools
        env_vars = {"CALCULATOR_ENABLE_ALL_TOOLS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            assert config_info["total_enabled_tools"] == 68
            assert config_info["configuration_source"] == "legacy"
        
        # New variables should override legacy
        env_vars = {
            "CALCULATOR_ENABLE_ALL_TOOLS": "true",
            "CALCULATOR_ENABLE_BASIC": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            assert len(config_info["enabled_groups"]) == 1
            assert "basic" in config_info["enabled_groups"]
            assert config_info["configuration_source"] == "individual"


class TestMultiplePresetConfigurations:
    """Test multiple preset configurations."""
    
    @pytest.mark.parametrize("config_name,env_vars", 
                           ConfigurationTestMatrix.MULTIPLE_PRESET_CONFIGS.items())
    def test_multiple_preset_configuration(self, config_name: str, env_vars: Dict[str, str]):
        """Test each multiple preset configuration."""
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Should combine all specified presets
            assert "preset_combined" in config_info["configuration_source"]
            
            # Should have more tools than any single preset
            if config_name == "scientific_business":
                # Should have tools from both scientific and business
                assert filter_obj.is_tool_enabled("derivative")  # scientific
                assert filter_obj.is_tool_enabled("compound_interest")  # business
            elif config_name == "all_presets":
                # Should have most tools (scientific + business + engineering overlap)
                assert len(config_info["enabled_groups"]) >= 8


class TestEdgeCaseConfigurations:
    """Test edge case configurations."""
    
    @pytest.mark.parametrize("config_name,env_vars", 
                           ConfigurationTestMatrix.EDGE_CASE_CONFIGS.items())
    def test_edge_case_configuration(self, config_name: str, env_vars: Dict[str, str]):
        """Test each edge case configuration."""
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            if config_name == "empty_config":
                # Should default to basic tools
                assert config_info["configuration_source"] == "default"
                assert config_info["enabled_groups"] == ["basic"]
                assert config_info["total_enabled_tools"] == 8
            
            elif config_name == "all_false":
                # Should still have basic tools (always enabled)
                assert "basic" in config_info["enabled_groups"]
                assert config_info["total_enabled_tools"] == 8  # Only basic tools
            
            elif config_name == "mixed_values":
                # Should handle mixed true/false/1/0 values correctly
                assert filter_obj.is_tool_enabled("add")  # basic (always enabled)
                assert not filter_obj.is_tool_enabled("trigonometric")  # advanced=false
                assert filter_obj.is_tool_enabled("descriptive_stats")  # statistics=1
                assert not filter_obj.is_tool_enabled("matrix_multiply")  # matrix=0
            
            elif config_name == "invalid_values":
                # Should handle invalid values gracefully
                assert len(config_info["warnings"]) >= 2  # Warnings for invalid values
                assert filter_obj.is_tool_enabled("descriptive_stats")  # statistics=true (valid)
                assert not filter_obj.is_tool_enabled("trigonometric")  # advanced=maybe (invalid)


class TestBooleanValueVariations:
    """Test boolean value variations."""
    
    def test_true_value_variations(self):
        """Test various ways to specify true values."""
        env_vars = ConfigurationTestMatrix.BOOLEAN_VALUE_CONFIGS["true_variations"]
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # All specified groups should be enabled due to various true values
            expected_tools = [
                "add",                  # basic (always enabled)
                "trigonometric",        # advanced=TRUE
                "descriptive_stats",    # statistics=True
                "matrix_multiply",      # matrix=1
                "complex_arithmetic",   # complex=yes
                "convert_units",        # units=YES
                "derivative",           # calculus=on
                "solve_linear",         # solver=ON
                "compound_interest",    # financial=enable
                "convert_currency"      # currency=enabled
            ]
            
            for tool in expected_tools:
                assert filter_obj.is_tool_enabled(tool), f"Tool {tool} should be enabled"
    
    def test_false_value_variations(self):
        """Test various ways to specify false values."""
        env_vars = ConfigurationTestMatrix.BOOLEAN_VALUE_CONFIGS["false_variations"]
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Should fall back to default (basic only) since all are false/disabled
            assert config_info["configuration_source"] == "default"
            assert config_info["enabled_groups"] == ["basic"]
            
            # Only basic tools should be enabled
            assert filter_obj.is_tool_enabled("add")
            assert not filter_obj.is_tool_enabled("trigonometric")
            assert not filter_obj.is_tool_enabled("matrix_multiply")


class TestConfigurationValidation:
    """Test configuration validation across all scenarios."""
    
    def test_all_configurations_are_valid(self):
        """Test that all configurations in the matrix are valid."""
        all_configs = ConfigurationTestMatrix.get_all_configurations()
        
        for config_name, env_vars in all_configs.items():
            with patch.dict(os.environ, env_vars, clear=True):
                try:
                    filter_obj = create_tool_filter_from_environment()
                    config_info = filter_obj.config.get_configuration_info()
                    
                    # Basic validation - should always have some tools enabled
                    assert config_info["total_enabled_tools"] > 0, f"Config {config_name} has no tools enabled"
                    assert len(config_info["enabled_groups"]) > 0, f"Config {config_name} has no groups enabled"
                    
                    # Should always have basic tools (they're always enabled now)
                    assert "basic" in config_info["enabled_groups"], f"Config {config_name} missing basic group"
                    
                except Exception as e:
                    pytest.fail(f"Configuration {config_name} failed: {e}")
    
    def test_configuration_consistency(self):
        """Test that configurations are internally consistent."""
        all_configs = ConfigurationTestMatrix.get_all_configurations()
        
        for config_name, env_vars in all_configs.items():
            with patch.dict(os.environ, env_vars, clear=True):
                filter_obj = create_tool_filter_from_environment()
                config_info = filter_obj.config.get_configuration_info()
                report = filter_obj.get_tool_availability_report()
                
                # Enabled + disabled should equal total
                total_from_groups = sum(info["total_tools"] for info in report["groups"].values())
                assert config_info["total_available_tools"] == total_from_groups
                
                # Enabled tools count should match
                enabled_from_groups = sum(info["enabled_count"] for info in report["groups"].values())
                assert config_info["total_enabled_tools"] == enabled_from_groups
                
                # Group counts should be consistent
                for group_name in config_info["enabled_groups"]:
                    assert report["groups"][group_name]["is_fully_enabled"] or report["groups"][group_name]["enabled_count"] > 0


class TestPerformanceMatrix:
    """Test performance across configuration matrix."""
    
    def test_configuration_loading_performance(self):
        """Test that all configurations load within reasonable time."""
        import time
        all_configs = ConfigurationTestMatrix.get_all_configurations()
        
        max_load_time = 0.1  # 100ms should be more than enough
        
        for config_name, env_vars in all_configs.items():
            with patch.dict(os.environ, env_vars, clear=True):
                start_time = time.time()
                filter_obj = create_tool_filter_from_environment()
                end_time = time.time()
                
                load_time = end_time - start_time
                assert load_time < max_load_time, f"Config {config_name} took {load_time:.3f}s to load"
    
    def test_tool_filtering_performance(self):
        """Test tool filtering performance across configurations."""
        import time
        
        # Create mock tool set
        mock_tools = {f"tool_{i}": lambda: f"result_{i}" for i in range(100)}
        
        all_configs = ConfigurationTestMatrix.get_all_configurations()
        max_filter_time = 0.05  # 50ms should be more than enough
        
        for config_name, env_vars in all_configs.items():
            with patch.dict(os.environ, env_vars, clear=True):
                filter_obj = create_tool_filter_from_environment()
                
                start_time = time.time()
                filtered_tools = filter_obj.filter_tools(mock_tools)
                end_time = time.time()
                
                filter_time = end_time - start_time
                assert filter_time < max_filter_time, f"Config {config_name} filtering took {filter_time:.3f}s"


class TestConfigurationDocumentation:
    """Test configuration documentation and help."""
    
    def test_all_configurations_have_clear_sources(self):
        """Test that all configurations have clear source identification."""
        all_configs = ConfigurationTestMatrix.get_all_configurations()
        
        for config_name, env_vars in all_configs.items():
            with patch.dict(os.environ, env_vars, clear=True):
                filter_obj = create_tool_filter_from_environment()
                config_info = filter_obj.config.get_configuration_info()
                
                # Should have a clear configuration source
                assert config_info["configuration_source"] is not None
                assert len(config_info["configuration_source"]) > 0
                
                # Source should be one of the expected types
                valid_sources = [
                    "default", "individual", "legacy",
                    "preset_all", "preset_scientific", "preset_business", "preset_engineering"
                ]
                
                source = config_info["configuration_source"]
                assert (source in valid_sources or 
                       source.startswith("preset_combined")), f"Unknown source: {source}"
    
    def test_error_messages_are_helpful(self):
        """Test that error messages provide helpful guidance."""
        # Test with basic configuration to get disabled tool errors
        with patch.dict(os.environ, {}, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Test error for each disabled group
            disabled_tools = [
                ("trigonometric", "advanced"),
                ("matrix_multiply", "matrix"),
                ("descriptive_stats", "statistics"),
                ("compound_interest", "financial")
            ]
            
            for tool_name, expected_group in disabled_tools:
                error_info = filter_obj.get_disabled_tool_error(tool_name)
                
                # Should have helpful error message
                assert "not available" in error_info["error"]
                assert expected_group in error_info["group_name"]
                
                # Should have actionable suggestions
                assert len(error_info["suggestions"]) >= 2
                assert any(f"CALCULATOR_ENABLE_{expected_group.upper()}" in suggestion 
                          for suggestion in error_info["suggestions"])
                assert any("CALCULATOR_ENABLE_ALL" in suggestion 
                          for suggestion in error_info["suggestions"])
                
                # Should have available alternatives
                assert len(error_info["available_alternatives"]) > 0
                for alt_tool in error_info["available_alternatives"]:
                    assert filter_obj.is_tool_enabled(alt_tool)