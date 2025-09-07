"""Tests for tool group management system."""

import os
import pytest
from unittest.mock import patch, MagicMock

from calculator.core.tool_groups import (
    ToolGroup,
    PresetCombination,
    ToolGroupRegistry,
    ToolGroupConfig
)
from calculator.core.tool_filter import ToolFilter, DisabledToolError


class TestToolGroupRegistry:
    """Test cases for ToolGroupRegistry."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolGroupRegistry()
    
    def test_initialization(self):
        """Test registry initialization."""
        assert len(self.registry.get_all_groups()) == 11
        assert ToolGroup.BASIC in self.registry.get_all_groups()
        assert self.registry.get_total_tool_count() == 68
    
    def test_get_tools_for_group(self):
        """Test getting tools for a specific group."""
        basic_tools = self.registry.get_tools_for_group(ToolGroup.BASIC)
        assert len(basic_tools) == 8
        assert "health_check" in basic_tools
        assert "add" in basic_tools
        assert "calculate" in basic_tools
        
        advanced_tools = self.registry.get_tools_for_group(ToolGroup.ADVANCED)
        assert len(advanced_tools) == 5
        assert "trigonometric" in advanced_tools
        assert "logarithm" in advanced_tools
    
    def test_get_group_for_tool(self):
        """Test getting group for a specific tool."""
        assert self.registry.get_group_for_tool("add") == ToolGroup.BASIC
        assert self.registry.get_group_for_tool("trigonometric") == ToolGroup.ADVANCED
        assert self.registry.get_group_for_tool("matrix_multiply") == ToolGroup.MATRIX
        assert self.registry.get_group_for_tool("nonexistent_tool") is None
    
    def test_get_group_description(self):
        """Test getting group descriptions."""
        basic_desc = self.registry.get_group_description(ToolGroup.BASIC)
        assert "arithmetic" in basic_desc.lower()
        
        advanced_desc = self.registry.get_group_description(ToolGroup.ADVANCED)
        assert "mathematical" in advanced_desc.lower()
    
    def test_is_default_enabled(self):
        """Test checking default enabled status."""
        assert self.registry.is_default_enabled(ToolGroup.BASIC) is True
        assert self.registry.is_default_enabled(ToolGroup.ADVANCED) is False
        assert self.registry.is_default_enabled(ToolGroup.STATISTICS) is False
    
    def test_preset_combinations(self):
        """Test preset combinations."""
        all_groups = self.registry.get_preset_groups(PresetCombination.ALL)
        assert len(all_groups) == 11
        
        scientific_groups = self.registry.get_preset_groups(PresetCombination.SCIENTIFIC)
        expected_scientific = [
            ToolGroup.BASIC, ToolGroup.ADVANCED, ToolGroup.STATISTICS,
            ToolGroup.MATRIX, ToolGroup.COMPLEX, ToolGroup.CALCULUS
        ]
        assert set(scientific_groups) == set(expected_scientific)
        
        business_groups = self.registry.get_preset_groups(PresetCombination.BUSINESS)
        expected_business = [
            ToolGroup.BASIC, ToolGroup.FINANCIAL, 
            ToolGroup.CURRENCY, ToolGroup.UNITS
        ]
        assert set(business_groups) == set(expected_business)
    
    def test_get_preset_info(self):
        """Test getting detailed preset information."""
        scientific_info = self.registry.get_preset_info(PresetCombination.SCIENTIFIC)
        assert scientific_info["name"] == PresetCombination.SCIENTIFIC
        assert scientific_info["group_count"] == 6
        assert scientific_info["total_tools"] > 30  # Should have many tools
        assert ToolGroup.BASIC in scientific_info["groups"]
        assert ToolGroup.CALCULUS in scientific_info["groups"]


class TestToolGroupConfig:
    """Test cases for ToolGroupConfig."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolGroupRegistry()
        self.config = ToolGroupConfig(self.registry)
    
    def test_default_configuration(self):
        """Test default configuration (no environment variables)."""
        with patch.dict(os.environ, {}, clear=True):
            self.config.load_from_environment()
            
            assert self.config.is_group_enabled(ToolGroup.BASIC)
            assert not self.config.is_group_enabled(ToolGroup.ADVANCED)
            assert self.config.configuration_source == "default"
            assert len(self.config.get_enabled_tools()) == 8  # Basic tools only
    
    def test_individual_group_configuration(self):
        """Test individual group environment variables."""
        env_vars = {
            "CALCULATOR_ENABLE_ADVANCED": "true",
            "CALCULATOR_ENABLE_MATRIX": "1"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            assert self.config.is_group_enabled(ToolGroup.BASIC)  # Always enabled
            assert self.config.is_group_enabled(ToolGroup.ADVANCED)
            assert self.config.is_group_enabled(ToolGroup.MATRIX)
            assert not self.config.is_group_enabled(ToolGroup.STATISTICS)
            assert self.config.configuration_source == "individual"
    
    def test_preset_all_configuration(self):
        """Test CALCULATOR_ENABLE_ALL preset."""
        env_vars = {"CALCULATOR_ENABLE_ALL": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            # All groups should be enabled
            for group in self.registry.get_all_groups():
                assert self.config.is_group_enabled(group)
            
            assert self.config.configuration_source == "preset_all"
            assert len(self.config.get_enabled_tools()) == 68
    
    def test_preset_scientific_configuration(self):
        """Test CALCULATOR_ENABLE_SCIENTIFIC preset."""
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            # Scientific groups should be enabled
            scientific_groups = self.registry.get_preset_groups(PresetCombination.SCIENTIFIC)
            for group in scientific_groups:
                assert self.config.is_group_enabled(group)
            
            # Non-scientific groups should be disabled
            assert not self.config.is_group_enabled(ToolGroup.FINANCIAL)
            assert not self.config.is_group_enabled(ToolGroup.CURRENCY)
            
            assert self.config.configuration_source == "preset_scientific"
    
    def test_preset_business_configuration(self):
        """Test CALCULATOR_ENABLE_BUSINESS preset."""
        env_vars = {"CALCULATOR_ENABLE_BUSINESS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            # Business groups should be enabled
            business_groups = self.registry.get_preset_groups(PresetCombination.BUSINESS)
            for group in business_groups:
                assert self.config.is_group_enabled(group)
            
            # Non-business groups should be disabled
            assert not self.config.is_group_enabled(ToolGroup.CALCULUS)
            assert not self.config.is_group_enabled(ToolGroup.MATRIX)
            
            assert self.config.configuration_source == "preset_business"
    
    def test_multiple_presets_configuration(self):
        """Test multiple preset combinations."""
        env_vars = {
            "CALCULATOR_ENABLE_SCIENTIFIC": "true",
            "CALCULATOR_ENABLE_BUSINESS": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            # Both scientific and business groups should be enabled
            scientific_groups = self.registry.get_preset_groups(PresetCombination.SCIENTIFIC)
            business_groups = self.registry.get_preset_groups(PresetCombination.BUSINESS)
            
            for group in scientific_groups + business_groups:
                assert self.config.is_group_enabled(group)
            
            assert "preset_combined" in self.config.configuration_source
    
    def test_legacy_configuration(self):
        """Test legacy CALCULATOR_ENABLE_ALL_TOOLS variable."""
        env_vars = {"CALCULATOR_ENABLE_ALL_TOOLS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            # All groups should be enabled
            for group in self.registry.get_all_groups():
                assert self.config.is_group_enabled(group)
            
            assert self.config.configuration_source == "legacy"
            assert len(self.config.warnings) > 0
            assert any("deprecated" in warning.lower() for warning in self.config.warnings)
    
    def test_legacy_precedence(self):
        """Test that new variables take precedence over legacy ones."""
        env_vars = {
            "CALCULATOR_ENABLE_ALL_TOOLS": "true",
            "CALCULATOR_ENABLE_ADVANCED": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            # Basic is always enabled, advanced should be enabled (new variable takes precedence)
            assert self.config.is_group_enabled(ToolGroup.BASIC)
            assert self.config.is_group_enabled(ToolGroup.ADVANCED)
            assert self.config.configuration_source == "individual"
    
    def test_boolean_value_parsing(self):
        """Test various boolean value formats."""
        test_cases = [
            ("true", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("enable", True),
            ("enabled", True),
            ("false", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("disable", False),
            ("disabled", False),
            ("", False),
            ("invalid", False)
        ]
        
        for value, expected in test_cases:
            env_vars = {"CALCULATOR_ENABLE_ADVANCED": value}
            
            with patch.dict(os.environ, env_vars, clear=True):
                config = ToolGroupConfig(self.registry)
                config.load_from_environment()
                
                if expected:
                    assert config.is_group_enabled(ToolGroup.ADVANCED), f"Failed for value: {value}"
                else:
                    assert not config.is_group_enabled(ToolGroup.ADVANCED), f"Failed for value: {value}"
    
    def test_invalid_boolean_warnings(self):
        """Test warnings for invalid boolean values."""
        env_vars = {"CALCULATOR_ENABLE_ADVANCED": "invalid_value"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            assert len(self.config.warnings) > 0
            assert any("invalid_value" in warning for warning in self.config.warnings)
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test with default configuration (no env vars)
        with patch.dict(os.environ, {}, clear=True):
            self.config.load_from_environment()
            
            # Should have basic tools enabled by default
            assert len(self.config.get_enabled_tools()) == 8
            assert self.config.is_group_enabled(ToolGroup.BASIC)
    
    def test_migration_recommendations(self):
        """Test migration recommendations."""
        # Test legacy variable recommendation
        env_vars = {"CALCULATOR_ENABLE_ALL_TOOLS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            recommendations = self.config.get_migration_recommendations()
            assert len(recommendations) > 0
            assert any("CALCULATOR_ENABLE_ALL" in rec for rec in recommendations)
    
    def test_get_configuration_info(self):
        """Test getting comprehensive configuration information."""
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            self.config.load_from_environment()
            
            info = self.config.get_configuration_info()
            
            assert "enabled_groups" in info
            assert "disabled_groups" in info
            assert "total_enabled_tools" in info
            assert "configuration_source" in info
            assert info["configuration_source"] == "preset_scientific"
            assert len(info["enabled_groups"]) == 6  # Scientific preset has 6 groups


class TestToolFilter:
    """Test cases for ToolFilter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ToolGroupRegistry()
        self.config = ToolGroupConfig(self.registry)
        
        # Configure for basic tools only
        with patch.dict(os.environ, {}, clear=True):
            self.config.load_from_environment()
        
        self.filter = ToolFilter(self.config, self.registry)
    
    def test_initialization(self):
        """Test filter initialization."""
        assert len(self.filter._enabled_tools) == 8  # Basic tools only
        assert self.filter.is_tool_enabled("add")
        assert not self.filter.is_tool_enabled("trigonometric")
    
    def test_filter_tools(self):
        """Test filtering tools dictionary."""
        all_tools = {
            "add": lambda: "add_result",
            "trigonometric": lambda: "trig_result",
            "matrix_multiply": lambda: "matrix_result",
            "health_check": lambda: "health_result"
        }
        
        filtered_tools = self.filter.filter_tools(all_tools)
        
        # Only basic tools should remain
        assert "add" in filtered_tools
        assert "health_check" in filtered_tools
        assert "trigonometric" not in filtered_tools
        assert "matrix_multiply" not in filtered_tools
        assert len(filtered_tools) == 2
    
    def test_is_tool_enabled(self):
        """Test checking if specific tools are enabled."""
        # Basic tools should be enabled
        assert self.filter.is_tool_enabled("add")
        assert self.filter.is_tool_enabled("subtract")
        assert self.filter.is_tool_enabled("health_check")
        
        # Advanced tools should be disabled
        assert not self.filter.is_tool_enabled("trigonometric")
        assert not self.filter.is_tool_enabled("matrix_multiply")
        assert not self.filter.is_tool_enabled("derivative")
    
    def test_get_disabled_tool_error(self):
        """Test getting error information for disabled tools."""
        # Test disabled tool
        error_info = self.filter.get_disabled_tool_error("trigonometric")
        
        assert error_info["error_type"] == "DisabledToolError"
        assert error_info["success"] is False
        assert error_info["tool_name"] == "trigonometric"
        assert error_info["group_name"] == ToolGroup.ADVANCED
        assert "CALCULATOR_ENABLE_ADVANCED" in error_info["suggestions"][0]
        assert len(error_info["available_alternatives"]) > 0
        
        # Test non-existent tool
        error_info = self.filter.get_disabled_tool_error("nonexistent_tool")
        
        assert error_info["error_type"] == "ToolNotFoundError"
        assert error_info["success"] is False
        assert "does not exist" in error_info["error"]
    
    def test_validate_tool_access(self):
        """Test validating tool access."""
        # Enabled tool should return None (no error)
        assert self.filter.validate_tool_access("add") is None
        
        # Disabled tool should return error info
        error_info = self.filter.validate_tool_access("trigonometric")
        assert error_info is not None
        assert error_info["error_type"] == "DisabledToolError"
    
    def test_get_filter_stats(self):
        """Test getting filter statistics."""
        stats = self.filter.get_filter_stats()
        
        assert stats["total_tools"] == 68
        assert stats["enabled_tools"] == 8
        assert stats["disabled_tools"] == 60
        assert stats["enabled_percentage"] == 11.8  # 8/68 * 100
        assert "basic" in stats["enabled_by_group"]
        assert stats["enabled_by_group"]["basic"] == 8
    
    def test_get_tool_availability_report(self):
        """Test getting comprehensive availability report."""
        report = self.filter.get_tool_availability_report()
        
        assert "summary" in report
        assert "groups" in report
        assert "enabled_tools" in report
        assert "disabled_tools" in report
        
        # Check basic group is fully enabled
        basic_group = report["groups"]["basic"]
        assert basic_group["is_fully_enabled"] is True
        assert basic_group["enabled_count"] == 8
        
        # Check advanced group is fully disabled
        advanced_group = report["groups"]["advanced"]
        assert advanced_group["is_fully_disabled"] is True
        assert advanced_group["disabled_count"] == 5


class TestToolFilterWithDifferentConfigurations:
    """Test ToolFilter with various configurations."""
    
    def test_scientific_configuration(self):
        """Test filter with scientific preset."""
        registry = ToolGroupRegistry()
        config = ToolGroupConfig(registry)
        
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            config.load_from_environment()
        
        filter_obj = ToolFilter(config, registry)
        
        # Scientific tools should be enabled
        assert filter_obj.is_tool_enabled("add")  # basic
        assert filter_obj.is_tool_enabled("trigonometric")  # advanced
        assert filter_obj.is_tool_enabled("descriptive_stats")  # statistics
        assert filter_obj.is_tool_enabled("matrix_multiply")  # matrix
        assert filter_obj.is_tool_enabled("complex_arithmetic")  # complex
        assert filter_obj.is_tool_enabled("derivative")  # calculus
        
        # Non-scientific tools should be disabled
        assert not filter_obj.is_tool_enabled("compound_interest")  # financial
        assert not filter_obj.is_tool_enabled("convert_currency")  # currency
    
    def test_all_tools_configuration(self):
        """Test filter with all tools enabled."""
        registry = ToolGroupRegistry()
        config = ToolGroupConfig(registry)
        
        env_vars = {"CALCULATOR_ENABLE_ALL": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            config.load_from_environment()
        
        filter_obj = ToolFilter(config, registry)
        
        # All tools should be enabled
        stats = filter_obj.get_filter_stats()
        assert stats["enabled_tools"] == 68
        assert stats["disabled_tools"] == 0
        assert stats["enabled_percentage"] == 100.0


def test_create_tool_filter_from_environment():
    """Test creating tool filter from environment variables."""
    from calculator.core.tool_filter import create_tool_filter_from_environment
    
    env_vars = {"CALCULATOR_ENABLE_BUSINESS": "true"}
    
    with patch.dict(os.environ, env_vars, clear=True):
        filter_obj = create_tool_filter_from_environment()
        
        # Business tools should be enabled
        assert filter_obj.is_tool_enabled("add")  # basic
        assert filter_obj.is_tool_enabled("compound_interest")  # financial
        assert filter_obj.is_tool_enabled("convert_currency")  # currency
        assert filter_obj.is_tool_enabled("convert_units")  # units
        
        # Non-business tools should be disabled
        assert not filter_obj.is_tool_enabled("derivative")  # calculus
        assert not filter_obj.is_tool_enabled("matrix_multiply")  # matrix


class TestDisabledToolError:
    """Test cases for DisabledToolError exception."""
    
    def test_disabled_tool_error_creation(self):
        """Test creating DisabledToolError."""
        error = DisabledToolError("trigonometric", "advanced")
        
        assert error.tool_name == "trigonometric"
        assert error.group_name == "advanced"
        assert "trigonometric" in error.message
        assert "advanced" in error.message
        assert str(error) == error.message


# Integration tests
class TestToolGroupIntegration:
    """Integration tests for the complete tool group system."""
    
    def test_end_to_end_basic_configuration(self):
        """Test complete workflow with basic configuration."""
        from calculator.core.tool_filter import create_tool_filter_from_environment
        
        # Clear environment to get default (basic only) configuration
        with patch.dict(os.environ, {}, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Verify configuration
            config_info = filter_obj.config.get_configuration_info()
            assert config_info["configuration_source"] == "default"
            assert len(config_info["enabled_groups"]) == 1
            assert "basic" in config_info["enabled_groups"]
            
            # Verify filtering
            assert filter_obj.is_tool_enabled("add")
            assert not filter_obj.is_tool_enabled("trigonometric")
            
            # Verify error handling
            error_info = filter_obj.get_disabled_tool_error("trigonometric")
            assert "CALCULATOR_ENABLE_ADVANCED" in str(error_info)
    
    def test_end_to_end_scientific_configuration(self):
        """Test complete workflow with scientific configuration."""
        from calculator.core.tool_filter import create_tool_filter_from_environment
        
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Verify configuration
            config_info = filter_obj.config.get_configuration_info()
            assert config_info["configuration_source"] == "preset_scientific"
            assert len(config_info["enabled_groups"]) == 6
            
            # Verify scientific tools are enabled
            scientific_tools = [
                "add", "trigonometric", "descriptive_stats", 
                "matrix_multiply", "complex_arithmetic", "derivative"
            ]
            for tool in scientific_tools:
                assert filter_obj.is_tool_enabled(tool)
            
            # Verify non-scientific tools are disabled
            non_scientific_tools = ["compound_interest", "convert_currency"]
            for tool in non_scientific_tools:
                assert not filter_obj.is_tool_enabled(tool)
    
    def test_configuration_validation_and_warnings(self):
        """Test configuration validation and warning system."""
        from calculator.core.tool_filter import create_tool_filter_from_environment
        
        # Test with legacy variable
        env_vars = {"CALCULATOR_ENABLE_ALL_TOOLS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            config_info = filter_obj.config.get_configuration_info()
            
            # Should have warnings about legacy usage
            assert len(config_info["warnings"]) > 0
            assert any("deprecated" in warning.lower() for warning in config_info["warnings"])
            
            # Should have migration recommendations
            recommendations = config_info["migration_recommendations"]
            assert len(recommendations) > 0
            assert any("CALCULATOR_ENABLE_ALL" in rec for rec in recommendations)