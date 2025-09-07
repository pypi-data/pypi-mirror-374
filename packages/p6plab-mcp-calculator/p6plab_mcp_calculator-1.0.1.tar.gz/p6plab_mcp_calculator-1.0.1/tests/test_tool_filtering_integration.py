"""Integration tests for tool filtering with MCP server."""

import os
import pytest
from unittest.mock import patch, MagicMock
import asyncio

from calculator.core.tool_filter import create_tool_filter_from_environment
from calculator.core.tool_groups import ToolGroup, PresetCombination


class TestMCPServerIntegration:
    """Integration tests for MCP server with tool filtering."""
    
    def test_server_startup_with_default_configuration(self):
        """Test server startup with default (basic only) configuration."""
        with patch.dict(os.environ, {}, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Verify only basic tools are enabled
            stats = filter_obj.get_filter_stats()
            assert stats["enabled_tools"] == 8
            assert stats["enabled_by_group"] == {"basic": 8}
            
            # Verify specific tools
            assert filter_obj.is_tool_enabled("health_check")
            assert filter_obj.is_tool_enabled("add")
            assert filter_obj.is_tool_enabled("calculate")
            assert not filter_obj.is_tool_enabled("trigonometric")
            assert not filter_obj.is_tool_enabled("matrix_multiply")
    
    def test_server_startup_with_scientific_configuration(self):
        """Test server startup with scientific preset."""
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Verify scientific tools are enabled
            stats = filter_obj.get_filter_stats()
            assert stats["enabled_tools"] > 30  # Should have many tools
            
            # Check specific scientific groups
            expected_groups = ["basic", "advanced", "statistics", "matrix", "complex", "calculus"]
            for group in expected_groups:
                assert group in stats["enabled_by_group"]
            
            # Verify specific tools
            scientific_tools = [
                "add", "trigonometric", "descriptive_stats",
                "matrix_multiply", "complex_arithmetic", "derivative"
            ]
            for tool in scientific_tools:
                assert filter_obj.is_tool_enabled(tool)
            
            # Verify non-scientific tools are disabled
            assert not filter_obj.is_tool_enabled("compound_interest")
            assert not filter_obj.is_tool_enabled("convert_currency")
    
    def test_server_startup_with_business_configuration(self):
        """Test server startup with business preset."""
        env_vars = {"CALCULATOR_ENABLE_BUSINESS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Verify business tools are enabled
            stats = filter_obj.get_filter_stats()
            
            # Check specific business groups
            expected_groups = ["basic", "financial", "currency", "units"]
            for group in expected_groups:
                assert group in stats["enabled_by_group"]
            
            # Verify specific tools
            business_tools = [
                "add", "compound_interest", "convert_currency", "convert_units"
            ]
            for tool in business_tools:
                assert filter_obj.is_tool_enabled(tool)
            
            # Verify non-business tools are disabled
            assert not filter_obj.is_tool_enabled("derivative")
            assert not filter_obj.is_tool_enabled("matrix_multiply")
    
    def test_server_startup_with_all_tools_configuration(self):
        """Test server startup with all tools enabled."""
        env_vars = {"CALCULATOR_ENABLE_ALL": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Verify all tools are enabled
            stats = filter_obj.get_filter_stats()
            assert stats["enabled_tools"] == 68
            assert stats["disabled_tools"] == 0
            assert stats["enabled_percentage"] == 100.0
            
            # All groups should be enabled
            assert len(stats["enabled_by_group"]) == 11
            assert "disabled_by_group" not in stats or len(stats["disabled_by_group"]) == 0
    
    def test_health_check_reporting(self):
        """Test health check tool reporting with different configurations."""
        # Test with scientific configuration
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Verify health check would report correct information
            assert config_info["configuration_source"] == "preset_scientific"
            assert len(config_info["enabled_groups"]) == 6
            assert "basic" in config_info["enabled_groups"]
            assert "calculus" in config_info["enabled_groups"]
            assert "financial" in config_info["disabled_groups"]
            assert "currency" in config_info["disabled_groups"]
    
    def test_disabled_tool_error_responses(self):
        """Test error responses for disabled tools."""
        # Configure with basic tools only
        with patch.dict(os.environ, {}, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Test disabled advanced tool
            error_info = filter_obj.get_disabled_tool_error("trigonometric")
            assert error_info["error_type"] == "DisabledToolError"
            assert error_info["tool_name"] == "trigonometric"
            assert error_info["group_name"] == "advanced"
            assert "CALCULATOR_ENABLE_ADVANCED=true" in error_info["suggestions"][0]
            
            # Test disabled matrix tool
            error_info = filter_obj.get_disabled_tool_error("matrix_multiply")
            assert error_info["error_type"] == "DisabledToolError"
            assert error_info["group_name"] == "matrix"
            assert "CALCULATOR_ENABLE_MATRIX=true" in error_info["suggestions"][0]
            
            # Test non-existent tool
            error_info = filter_obj.get_disabled_tool_error("nonexistent_tool")
            assert error_info["error_type"] == "ToolNotFoundError"
            assert "does not exist" in error_info["error"]
    
    def test_tool_availability_report(self):
        """Test comprehensive tool availability reporting."""
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            report = filter_obj.get_tool_availability_report()
            
            # Verify report structure
            assert "summary" in report
            assert "groups" in report
            assert "enabled_tools" in report
            assert "disabled_tools" in report
            
            # Verify group details
            for group_name, group_info in report["groups"].items():
                assert "description" in group_info
                assert "total_tools" in group_info
                assert "enabled_tools" in group_info
                assert "disabled_tools" in group_info
                assert "is_fully_enabled" in group_info
                assert "is_fully_disabled" in group_info
            
            # Verify scientific groups are fully enabled
            scientific_groups = ["basic", "advanced", "statistics", "matrix", "complex", "calculus"]
            for group in scientific_groups:
                assert report["groups"][group]["is_fully_enabled"]
            
            # Verify non-scientific groups are fully disabled
            non_scientific_groups = ["financial", "currency"]
            for group in non_scientific_groups:
                assert report["groups"][group]["is_fully_disabled"]


class TestConfigurationValidation:
    """Test configuration validation and error handling."""
    
    def test_invalid_environment_variables(self):
        """Test handling of invalid environment variable values."""
        env_vars = {
            "CALCULATOR_ENABLE_ADVANCED": "invalid_value",
            "CALCULATOR_ENABLE_MATRIX": "maybe",
            "CALCULATOR_ENABLE_STATISTICS": "true"  # This one is valid
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Should have warnings about invalid values
            assert len(config_info["warnings"]) >= 2
            warning_text = " ".join(config_info["warnings"])
            assert "invalid_value" in warning_text
            assert "maybe" in warning_text
            
            # Only statistics and basic should be enabled (invalid values treated as false)
            assert filter_obj.is_tool_enabled("descriptive_stats")  # statistics
            assert filter_obj.is_tool_enabled("add")  # basic (default)
            assert not filter_obj.is_tool_enabled("trigonometric")  # advanced (invalid)
            assert not filter_obj.is_tool_enabled("matrix_multiply")  # matrix (invalid)
    
    def test_legacy_variable_warnings(self):
        """Test warnings for legacy environment variables."""
        env_vars = {"CALCULATOR_ENABLE_ALL_TOOLS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Should have legacy warnings
            assert len(config_info["warnings"]) > 0
            warning_text = " ".join(config_info["warnings"])
            assert "deprecated" in warning_text.lower()
            assert "CALCULATOR_ENABLE_ALL_TOOLS" in warning_text
            
            # Should have migration recommendations
            recommendations = config_info["migration_recommendations"]
            assert len(recommendations) > 0
            rec_text = " ".join(recommendations)
            assert "CALCULATOR_ENABLE_ALL" in rec_text
    
    def test_precedence_handling(self):
        """Test precedence of different configuration methods."""
        # Test that new variables take precedence over legacy
        env_vars = {
            "CALCULATOR_ENABLE_ALL_TOOLS": "true",  # Legacy - should be ignored
            "CALCULATOR_ENABLE_ADVANCED": "true"    # New - should take precedence
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Basic and advanced should be enabled
            assert filter_obj.is_tool_enabled("add")  # basic (always enabled)
            assert filter_obj.is_tool_enabled("trigonometric")  # advanced (explicitly enabled)
            
            config_info = filter_obj.config.get_configuration_info()
            assert config_info["configuration_source"] == "individual"
        
        # Test that presets take precedence over individual settings
        env_vars = {
            "CALCULATOR_ENABLE_ADVANCED": "true",
            "CALCULATOR_ENABLE_MATRIX": "true",
            "CALCULATOR_ENABLE_ALL": "true"  # This should take precedence
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # All tools should be enabled due to preset
            stats = filter_obj.get_filter_stats()
            assert stats["enabled_tools"] == 68
            
            config_info = filter_obj.config.get_configuration_info()
            assert config_info["configuration_source"] == "preset_all"


class TestMultiplePresetCombinations:
    """Test multiple preset combinations."""
    
    def test_scientific_plus_business_presets(self):
        """Test combining scientific and business presets."""
        env_vars = {
            "CALCULATOR_ENABLE_SCIENTIFIC": "true",
            "CALCULATOR_ENABLE_BUSINESS": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Should have tools from both presets
            scientific_tools = ["trigonometric", "matrix_multiply", "derivative"]
            business_tools = ["compound_interest", "convert_currency"]
            
            for tool in scientific_tools + business_tools:
                assert filter_obj.is_tool_enabled(tool)
            
            config_info = filter_obj.config.get_configuration_info()
            assert "preset_combined" in config_info["configuration_source"]
    
    def test_engineering_preset(self):
        """Test engineering preset configuration."""
        env_vars = {"CALCULATOR_ENABLE_ENGINEERING": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Engineering should include: basic, advanced, matrix, complex, calculus, units, constants
            engineering_tools = [
                "add",              # basic
                "trigonometric",    # advanced
                "matrix_multiply",  # matrix
                "complex_arithmetic", # complex
                "derivative",       # calculus
                "convert_units",    # units
                "get_constant"      # constants
            ]
            
            for tool in engineering_tools:
                assert filter_obj.is_tool_enabled(tool)
            
            # Should not include financial or currency
            assert not filter_obj.is_tool_enabled("compound_interest")
            assert not filter_obj.is_tool_enabled("convert_currency")
            
            config_info = filter_obj.config.get_configuration_info()
            assert config_info["configuration_source"] == "preset_engineering"


class TestPerformanceAndScaling:
    """Test performance aspects of tool filtering."""
    
    def test_filter_performance_with_large_tool_set(self):
        """Test filtering performance with all 68 tools."""
        # Create a mock tool set with all 68 tools
        all_tools = {}
        filter_obj = create_tool_filter_from_environment()
        
        # Get all possible tool names
        registry = filter_obj.registry
        for group_name in registry.get_all_groups():
            for tool_name in registry.get_tools_for_group(group_name):
                all_tools[tool_name] = lambda: f"result_for_{tool_name}"
        
        # Test filtering with different configurations
        configurations = [
            {},  # Default (basic only)
            {"CALCULATOR_ENABLE_SCIENTIFIC": "true"},
            {"CALCULATOR_ENABLE_ALL": "true"}
        ]
        
        for env_config in configurations:
            with patch.dict(os.environ, env_config, clear=True):
                filter_obj = create_tool_filter_from_environment()
                
                # Filtering should be fast
                import time
                start_time = time.time()
                filtered_tools = filter_obj.filter_tools(all_tools)
                end_time = time.time()
                
                # Should complete in reasonable time (< 0.1 seconds)
                assert (end_time - start_time) < 0.1
                
                # Verify correct number of tools
                stats = filter_obj.get_filter_stats()
                assert len(filtered_tools) == stats["enabled_tools"]
    
    def test_memory_usage_with_different_configurations(self):
        """Test memory usage patterns with different configurations."""
        import sys
        
        configurations = [
            ({}, "basic"),
            ({"CALCULATOR_ENABLE_SCIENTIFIC": "true"}, "scientific"),
            ({"CALCULATOR_ENABLE_ALL": "true"}, "all")
        ]
        
        memory_usage = {}
        
        for env_config, config_name in configurations:
            with patch.dict(os.environ, env_config, clear=True):
                filter_obj = create_tool_filter_from_environment()
                
                # Get approximate memory usage
                # This is a rough estimate - in practice you'd use more sophisticated profiling
                config_size = sys.getsizeof(filter_obj.config)
                filter_size = sys.getsizeof(filter_obj)
                
                memory_usage[config_name] = {
                    "config_size": config_size,
                    "filter_size": filter_size,
                    "enabled_tools": len(filter_obj._enabled_tools)
                }
        
        # Memory usage should scale reasonably with number of enabled tools
        assert memory_usage["basic"]["enabled_tools"] < memory_usage["scientific"]["enabled_tools"]
        assert memory_usage["scientific"]["enabled_tools"] < memory_usage["all"]["enabled_tools"]


class TestErrorHandlingAndRecovery:
    """Test error handling and recovery scenarios."""
    
    def test_malformed_environment_variables(self):
        """Test handling of malformed environment variables."""
        env_vars = {
            "CALCULATOR_ENABLE_ADVANCED": "   ",  # Whitespace only
            "CALCULATOR_ENABLE_MATRIX": "TRUE ",  # Trailing space
            "CALCULATOR_ENABLE_STATISTICS": " true",  # Leading space
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Should handle gracefully
            assert filter_obj.is_tool_enabled("add")  # Basic should always be enabled
            assert filter_obj.is_tool_enabled("matrix_multiply")  # Should handle "TRUE "
            assert filter_obj.is_tool_enabled("descriptive_stats")  # Should handle " true"
            assert not filter_obj.is_tool_enabled("trigonometric")  # Whitespace should be false
    
    def test_configuration_recovery_from_errors(self):
        """Test configuration recovery from various error conditions."""
        # Test with completely invalid configuration
        env_vars = {
            "CALCULATOR_ENABLE_ADVANCED": "also_invalid",
            "CALCULATOR_ENABLE_MATRIX": "nope",
            "CALCULATOR_ENABLE_STATISTICS": "invalid"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Should fall back to default (basic tools only)
            assert filter_obj.is_tool_enabled("add")  # Basic always enabled
            assert not filter_obj.is_tool_enabled("trigonometric")  # Invalid values treated as false
            
            config_info = filter_obj.config.get_configuration_info()
            assert config_info["configuration_source"] == "default"
            assert len(config_info["warnings"]) >= 3  # Should warn about all invalid values
    
    def test_partial_configuration_errors(self):
        """Test handling of partial configuration errors."""
        env_vars = {
            "CALCULATOR_ENABLE_ADVANCED": "invalid", # Invalid
            "CALCULATOR_ENABLE_MATRIX": "true"      # Valid
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Valid configurations should work
            assert filter_obj.is_tool_enabled("add")  # basic (always enabled)
            assert filter_obj.is_tool_enabled("matrix_multiply")  # matrix (valid)
            
            # Invalid configuration should be ignored
            assert not filter_obj.is_tool_enabled("trigonometric")  # advanced (invalid)
            
            config_info = filter_obj.config.get_configuration_info()
            assert "basic" in config_info["enabled_groups"]
            assert "matrix" in config_info["enabled_groups"]
            assert "advanced" not in config_info["enabled_groups"]
            assert len(config_info["warnings"]) >= 1  # Should warn about invalid value


class TestDocumentationAndUsability:
    """Test documentation and usability features."""
    
    def test_comprehensive_error_messages(self):
        """Test that error messages are comprehensive and helpful."""
        with patch.dict(os.environ, {}, clear=True):
            filter_obj = create_tool_filter_from_environment()
            
            # Test error message for disabled tool
            error_info = filter_obj.get_disabled_tool_error("trigonometric")
            
            # Should include all necessary information
            assert "trigonometric" in error_info["error"]
            assert "advanced" in error_info["group_name"]
            assert "CALCULATOR_ENABLE_ADVANCED=true" in error_info["suggestions"][0]
            assert "CALCULATOR_ENABLE_ALL=true" in error_info["suggestions"][1]
            assert len(error_info["available_alternatives"]) > 0
            
            # Alternatives should be actually available
            for alt_tool in error_info["available_alternatives"]:
                assert filter_obj.is_tool_enabled(alt_tool)
    
    def test_configuration_help_and_guidance(self):
        """Test configuration help and guidance features."""
        # Test with legacy configuration
        env_vars = {"CALCULATOR_ENABLE_ALL_TOOLS": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            config_info = filter_obj.config.get_configuration_info()
            
            # Should provide clear migration guidance
            recommendations = config_info["migration_recommendations"]
            assert len(recommendations) > 0
            
            migration_text = " ".join(recommendations)
            assert "CALCULATOR_ENABLE_ALL_TOOLS" in migration_text
            assert "CALCULATOR_ENABLE_ALL" in migration_text
    
    def test_availability_report_completeness(self):
        """Test that availability reports are complete and informative."""
        env_vars = {"CALCULATOR_ENABLE_SCIENTIFIC": "true"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            filter_obj = create_tool_filter_from_environment()
            report = filter_obj.get_tool_availability_report()
            
            # Should have complete information for all groups
            assert len(report["groups"]) == 11  # All tool groups
            
            for group_name, group_info in report["groups"].items():
                # Each group should have complete information
                assert "description" in group_info
                assert "total_tools" in group_info
                assert "enabled_tools" in group_info
                assert "disabled_tools" in group_info
                assert "enabled_count" in group_info
                assert "disabled_count" in group_info
                assert "is_fully_enabled" in group_info
                assert "is_fully_disabled" in group_info
                
                # Counts should be consistent
                assert group_info["enabled_count"] == len(group_info["enabled_tools"])
                assert group_info["disabled_count"] == len(group_info["disabled_tools"])
                assert (group_info["enabled_count"] + group_info["disabled_count"]) == group_info["total_tools"]