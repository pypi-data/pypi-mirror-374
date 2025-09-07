"""
Tool Filter System

This module provides functionality to filter available tools based on 
tool group configuration and handle disabled tool access attempts.
"""

from typing import List, Dict, Any, Optional, Callable
import logging
import time
from .tool_groups import ToolGroupConfig, ToolGroupRegistry

logger = logging.getLogger(__name__)


class DisabledToolError(Exception):
    """Exception raised when attempting to access a disabled tool."""
    
    def __init__(self, tool_name: str, group_name: str):
        self.tool_name = tool_name
        self.group_name = group_name
        self.message = (
            f"Tool '{tool_name}' is not available. "
            f"Enable the '{group_name}' group to access this tool."
        )
        super().__init__(self.message)


class ToolFilter:
    """Filters available tools based on tool group configuration."""
    
    def __init__(self, config: ToolGroupConfig, registry: Optional[ToolGroupRegistry] = None):
        """Initialize tool filter with configuration and registry."""
        self.config = config
        self.registry = registry or ToolGroupRegistry()
        self._enabled_tools = set(config.get_enabled_tools())
        self._access_attempts = {}  # Track access attempts to disabled tools
        self._filter_stats = {}     # Track filtering statistics
        
        logger.info(f"ToolFilter initialized with {len(self._enabled_tools)} enabled tools")
    
    def filter_tools(self, all_tools: Dict[str, Callable]) -> Dict[str, Callable]:
        """Filter tools dictionary to include only enabled tools."""
        filtered_tools = {}
        
        for tool_name, tool_func in all_tools.items():
            if self.is_tool_enabled(tool_name):
                filtered_tools[tool_name] = tool_func
            else:
                logger.debug(f"Filtered out disabled tool: {tool_name}")
        
        logger.info(f"Filtered tools: {len(filtered_tools)} enabled out of {len(all_tools)} total")
        return filtered_tools
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled."""
        return tool_name in self._enabled_tools
    
    def get_disabled_tool_error(self, tool_name: str) -> Dict[str, Any]:
        """Get structured error response for disabled tool access."""
        # Track access attempt to disabled tool
        self._track_disabled_access_attempt(tool_name)
        
        group_name = self.registry.get_group_for_tool(tool_name)
        
        if group_name is None:
            # Tool doesn't exist at all
            logger.warning(f"Access attempt to non-existent tool: {tool_name}")
            return {
                "error": f"Tool '{tool_name}' does not exist",
                "error_type": "ToolNotFoundError",
                "success": False,
                "tool_name": tool_name,
                "suggestions": [
                    "Check available tools using health_check",
                    "Verify tool name spelling"
                ]
            }
        
        # Tool exists but is disabled
        group_description = self.registry.get_group_description(group_name)
        env_var = f"CALCULATOR_ENABLE_{group_name.upper()}"
        
        logger.info(f"Access attempt to disabled tool: {tool_name} (group: {group_name})")
        
        return {
            "error": f"Tool '{tool_name}' is not available. Enable the '{group_name}' group to access this tool.",
            "error_type": "DisabledToolError",
            "success": False,
            "tool_name": tool_name,
            "group_name": group_name,
            "group_description": group_description,
            "suggestions": [
                f"Set environment variable {env_var}=true to enable this tool",
                f"Or use CALCULATOR_ENABLE_ALL=true to enable all tools",
                "Check available tools using health_check"
            ],
            "available_alternatives": self._get_available_alternatives(tool_name)
        }
    
    def _get_available_alternatives(self, tool_name: str) -> List[str]:
        """Get list of available tools that might be alternatives."""
        alternatives = []
        
        # Always include basic arithmetic as safe alternatives
        basic_tools = self.registry.get_tools_for_group("basic")
        alternatives.extend([tool for tool in basic_tools if self.is_tool_enabled(tool)])
        
        # Try to find tools from the same category if any are enabled
        tool_group = self.registry.get_group_for_tool(tool_name)
        if tool_group:
            group_tools = self.registry.get_tools_for_group(tool_group)
            enabled_in_group = [tool for tool in group_tools if self.is_tool_enabled(tool)]
            alternatives.extend(enabled_in_group)
        
        # Remove duplicates and the requested tool itself
        alternatives = list(set(alternatives))
        if tool_name in alternatives:
            alternatives.remove(tool_name)
        
        return sorted(alternatives)
    
    def validate_tool_access(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Validate tool access and return error if disabled."""
        if not self.is_tool_enabled(tool_name):
            return self.get_disabled_tool_error(tool_name)
        return None
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get statistics about tool filtering."""
        total_tools = self.registry.get_total_tool_count()
        enabled_count = len(self._enabled_tools)
        disabled_count = total_tools - enabled_count
        
        enabled_by_group = {}
        disabled_by_group = {}
        
        for group_name in self.registry.get_all_groups():
            group_tools = self.registry.get_tools_for_group(group_name)
            enabled_in_group = [t for t in group_tools if self.is_tool_enabled(t)]
            disabled_in_group = [t for t in group_tools if not self.is_tool_enabled(t)]
            
            if enabled_in_group:
                enabled_by_group[group_name] = len(enabled_in_group)
            if disabled_in_group:
                disabled_by_group[group_name] = len(disabled_in_group)
        
        return {
            "total_tools": total_tools,
            "enabled_tools": enabled_count,
            "disabled_tools": disabled_count,
            "enabled_percentage": round((enabled_count / total_tools) * 100, 1),
            "enabled_by_group": enabled_by_group,
            "disabled_by_group": disabled_by_group
        }


    def _track_disabled_access_attempt(self, tool_name: str) -> None:
        """Track access attempts to disabled tools for monitoring."""
        if tool_name not in self._access_attempts:
            self._access_attempts[tool_name] = {
                "count": 0,
                "first_attempt": None,
                "last_attempt": None,
                "group": self.registry.get_group_for_tool(tool_name)
            }
        
        import time
        current_time = time.time()
        
        self._access_attempts[tool_name]["count"] += 1
        self._access_attempts[tool_name]["last_attempt"] = current_time
        
        if self._access_attempts[tool_name]["first_attempt"] is None:
            self._access_attempts[tool_name]["first_attempt"] = current_time
    
    def get_access_monitoring_report(self) -> Dict[str, Any]:
        """Get report of disabled tool access attempts for monitoring."""
        if not self._access_attempts:
            return {
                "total_attempts": 0,
                "unique_tools_attempted": 0,
                "attempts_by_tool": {},
                "attempts_by_group": {},
                "recommendations": []
            }
        
        attempts_by_group = {}
        total_attempts = 0
        
        for tool_name, attempt_info in self._access_attempts.items():
            total_attempts += attempt_info["count"]
            group_name = attempt_info["group"] or "unknown"
            
            if group_name not in attempts_by_group:
                attempts_by_group[group_name] = {
                    "count": 0,
                    "tools": []
                }
            
            attempts_by_group[group_name]["count"] += attempt_info["count"]
            attempts_by_group[group_name]["tools"].append(tool_name)
        
        # Generate recommendations based on access patterns
        recommendations = []
        for group_name, group_attempts in attempts_by_group.items():
            if group_attempts["count"] >= 3:  # Threshold for recommendation
                recommendations.append(
                    f"Consider enabling '{group_name}' group - {group_attempts['count']} access attempts to {len(group_attempts['tools'])} tools"
                )
        
        return {
            "total_attempts": total_attempts,
            "unique_tools_attempted": len(self._access_attempts),
            "attempts_by_tool": {
                tool: {
                    "count": info["count"],
                    "group": info["group"],
                    "first_attempt": info["first_attempt"],
                    "last_attempt": info["last_attempt"]
                }
                for tool, info in self._access_attempts.items()
            },
            "attempts_by_group": attempts_by_group,
            "recommendations": recommendations
        }
    
    def reset_access_monitoring(self) -> None:
        """Reset access monitoring statistics."""
        self._access_attempts.clear()
        logger.info("Access monitoring statistics reset")
    
    def get_tool_availability_report(self) -> Dict[str, Any]:
        """Get comprehensive report of tool availability by group."""
        report = {
            "summary": self.get_filter_stats(),
            "groups": {},
            "enabled_tools": sorted(self._enabled_tools),
            "disabled_tools": []
        }
        
        all_disabled_tools = []
        
        for group_name in self.registry.get_all_groups():
            group_tools = self.registry.get_tools_for_group(group_name)
            enabled_tools = [t for t in group_tools if self.is_tool_enabled(t)]
            disabled_tools = [t for t in group_tools if not self.is_tool_enabled(t)]
            
            all_disabled_tools.extend(disabled_tools)
            
            report["groups"][group_name] = {
                "description": self.registry.get_group_description(group_name),
                "total_tools": len(group_tools),
                "enabled_tools": enabled_tools,
                "disabled_tools": disabled_tools,
                "enabled_count": len(enabled_tools),
                "disabled_count": len(disabled_tools),
                "is_fully_enabled": len(disabled_tools) == 0,
                "is_fully_disabled": len(enabled_tools) == 0
            }
        
        report["disabled_tools"] = sorted(all_disabled_tools)
        
        # Add access monitoring information
        access_report = self.get_access_monitoring_report()
        report["access_monitoring"] = access_report
        
        return report
    
    def get_comprehensive_monitoring_report(self) -> Dict[str, Any]:
        """Get comprehensive monitoring report including configuration and access patterns."""
        config_info = self.config.get_configuration_info()
        availability_report = self.get_tool_availability_report()
        filter_stats = self.get_filter_stats()
        
        return {
            "timestamp": time.time(),
            "configuration": {
                "source": config_info["configuration_source"],
                "enabled_groups": config_info["enabled_groups"],
                "disabled_groups": config_info["disabled_groups"],
                "warnings": config_info.get("warnings", []),
                "recommendations": config_info.get("migration_recommendations", [])
            },
            "tool_statistics": {
                "total_tools": filter_stats["total_tools"],
                "enabled_tools": filter_stats["enabled_tools"],
                "disabled_tools": filter_stats["disabled_tools"],
                "enabled_percentage": filter_stats["enabled_percentage"],
                "enabled_by_group": filter_stats["enabled_by_group"],
                "disabled_by_group": filter_stats.get("disabled_by_group", {})
            },
            "access_monitoring": availability_report["access_monitoring"],
            "group_details": availability_report["groups"]
        }


def create_tool_filter_from_environment() -> ToolFilter:
    """Create a ToolFilter instance configured from environment variables."""
    registry = ToolGroupRegistry()
    config = ToolGroupConfig(registry)
    config.load_from_environment()
    return ToolFilter(config, registry)