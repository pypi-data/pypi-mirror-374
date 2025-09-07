# Implementation Plan

- [x] 1. Create core tool group infrastructure
  - Implement ToolGroupRegistry class with predefined tool group mappings
  - Create ToolGroupConfig class for environment variable parsing and validation
  - Add tool group definitions with all 11 categories and their respective tools
  - _Requirements: 1.1, 2.1-2.11_

- [x] 2. Implement environment variable configuration system
  - [x] 2.1 Create environment variable parser for individual group controls
    - Parse CALCULATOR_ENABLE_* variables for each tool group
    - Implement boolean value parsing (true/false, 1/0) with validation
    - Add error handling for invalid environment variable values
    - _Requirements: 2.1-2.11, 5.5_

  - [x] 2.2 Add preset combination support
    - Implement CALCULATOR_ENABLE_ALL for enabling all 68 tools
    - Add CALCULATOR_ENABLE_SCIENTIFIC preset (basic, advanced, statistics, matrix, complex, calculus)
    - Add CALCULATOR_ENABLE_BUSINESS preset (basic, financial, currency, units)
    - Add CALCULATOR_ENABLE_ENGINEERING preset (basic, advanced, matrix, complex, calculus, units, constants)
    - _Requirements: 4.1-4.5_

  - [x] 2.3 Implement legacy compatibility support
    - Add support for existing CALCULATOR_ENABLE_ALL_TOOLS environment variable
    - Implement precedence logic (new variables override legacy variables)
    - Add deprecation warnings for legacy environment variables
    - _Requirements: 6.1-6.4_

- [x] 3. Create tool filtering mechanism
  - [x] 3.1 Implement ToolFilter class for runtime tool management
    - Create tool filtering logic based on enabled groups
    - Implement is_tool_enabled method for runtime checks
    - Add get_disabled_tool_error method for proper error responses
    - _Requirements: 3.1-3.3, 5.1-5.2_

  - [x] 3.2 Add default configuration handling
    - Ensure basic arithmetic tools are always enabled by default
    - Implement fallback logic when no environment variables are set
    - Add configuration validation to prevent zero-tool scenarios
    - _Requirements: 1.1, 6.1_

- [x] 4. Integrate tool filtering with MCP server
  - [x] 4.1 Modify MCP server registration to use filtered tools
    - Update server.py to apply tool filtering during startup
    - Ensure only enabled tools are registered with FastMCP
    - Add startup logging for enabled/disabled tool groups
    - _Requirements: 3.1, 5.3_

  - [x] 4.2 Implement disabled tool error handling
    - Add middleware to catch calls to disabled tools
    - Return structured error responses for disabled tool access
    - Ensure "tool not found" errors for unregistered tools
    - _Requirements: 3.2, 5.2_

- [x] 5. Enhance health check functionality
  - [x] 5.1 Update health_check tool to report group status
    - Add enabled_groups and disabled_groups to health check response
    - Include total_tools count and tool_counts_by_group breakdown
    - Add configuration_source information (environment, preset, legacy)
    - _Requirements: 3.3_

  - [x] 5.2 Add configuration validation and warnings
    - Implement validation for tool group names and values
    - Add warning collection for invalid configurations
    - Include warnings in health check response
    - _Requirements: 1.5, 5.5_

- [x] 6. Create comprehensive test suite
  - [x] 6.1 Write unit tests for configuration parsing
    - Test individual group environment variable parsing
    - Test preset combination logic and precedence
    - Test legacy compatibility and migration scenarios
    - _Requirements: 2.1-2.11, 4.1-4.5, 6.1-6.4_

  - [x] 6.2 Write integration tests for tool filtering
    - Test MCP server registration with various configurations
    - Test tool availability and disabled tool error responses
    - Test health check reporting accuracy
    - _Requirements: 3.1-3.3, 5.1-5.3_

  - [x] 6.3 Create configuration test matrix
    - Test all preset combinations (scientific, business, engineering, all)
    - Test custom group combinations and edge cases
    - Test backward compatibility scenarios
    - _Requirements: 1.1-1.5, 4.1-4.5, 6.1-6.4_

- [x] 7. Update documentation and configuration examples
  - [x] 7.1 Update installation and deployment documentation
    - Add environment variable configuration examples to docs/installation.md
    - Update MCP client configuration examples with tool group settings
    - Add troubleshooting section for tool group configuration issues
    - _Requirements: 6.4_

  - [x] 7.2 Create configuration guide and migration documentation
    - Document all available environment variables and their effects
    - Create migration guide for existing deployments
    - Add examples for common use cases (minimal, scientific, business, full)
    - _Requirements: 6.4_

- [x] 8. Implement logging and monitoring enhancements
  - [x] 8.1 Add startup configuration logging
    - Log enabled and disabled tool groups at server startup
    - Log total tool count and breakdown by group
    - Add warnings for invalid configurations or deprecated variables
    - _Requirements: 5.3, 5.5_

  - [x] 8.2 Add runtime monitoring for disabled tool access attempts
    - Log attempts to access disabled tools for monitoring
    - Track configuration effectiveness and usage patterns
    - Add metrics for tool group utilization
    - _Requirements: 5.2_