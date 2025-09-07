# Requirements Document

## Introduction

This feature adds the ability to selectively enable or disable groups of mathematical tools in the Scientific Calculator MCP Server based on environment variables. By default, only basic calculator tools will be enabled, allowing users to opt-in to additional mathematical capabilities as needed. This provides better resource management, security control, and deployment flexibility for different use cases.

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to control which mathematical tool groups are available in the MCP server, so that I can limit functionality based on security policies and resource constraints.

#### Acceptance Criteria

1. WHEN the server starts WITHOUT any tool group environment variables THEN the system SHALL enable only the basic arithmetic tools (add, subtract, multiply, divide, power, square_root, calculate, health_check)
2. WHEN a tool group environment variable is set to "true" or "1" THEN the system SHALL enable all tools in that specific group
3. WHEN a tool group environment variable is set to "false" or "0" THEN the system SHALL disable all tools in that specific group
4. WHEN multiple tool group environment variables are enabled THEN the system SHALL enable all tools from all specified groups
5. WHEN an invalid tool group name is specified THEN the system SHALL log a warning and ignore the invalid group

### Requirement 2

**User Story:** As a developer, I want to configure tool groups through environment variables, so that I can easily control available functionality without code changes.

#### Acceptance Criteria

1. WHEN I set CALCULATOR_ENABLE_BASIC=true THEN the system SHALL enable basic arithmetic tools (8 tools)
2. WHEN I set CALCULATOR_ENABLE_ADVANCED=true THEN the system SHALL enable advanced mathematics tools (5 tools)
3. WHEN I set CALCULATOR_ENABLE_STATISTICS=true THEN the system SHALL enable statistics tools (5 tools)
4. WHEN I set CALCULATOR_ENABLE_MATRIX=true THEN the system SHALL enable matrix operations tools (8 tools)
5. WHEN I set CALCULATOR_ENABLE_COMPLEX=true THEN the system SHALL enable complex number tools (6 tools)
6. WHEN I set CALCULATOR_ENABLE_UNITS=true THEN the system SHALL enable unit conversion tools (7 tools)
7. WHEN I set CALCULATOR_ENABLE_CALCULUS=true THEN the system SHALL enable calculus tools (9 tools)
8. WHEN I set CALCULATOR_ENABLE_SOLVER=true THEN the system SHALL enable equation solving tools (6 tools)
9. WHEN I set CALCULATOR_ENABLE_FINANCIAL=true THEN the system SHALL enable financial mathematics tools (7 tools)
10. WHEN I set CALCULATOR_ENABLE_CURRENCY=true THEN the system SHALL enable currency conversion tools (4 tools)
11. WHEN I set CALCULATOR_ENABLE_CONSTANTS=true THEN the system SHALL enable constants and references tools (3 tools)

### Requirement 3

**User Story:** As a user, I want to see only the tools that are enabled for my deployment, so that I don't get confused by unavailable functionality.

#### Acceptance Criteria

1. WHEN I query available tools through MCP THEN the system SHALL return only the tools from enabled groups
2. WHEN I attempt to use a tool from a disabled group THEN the system SHALL return an error indicating the tool is not available
3. WHEN I use the health_check tool THEN the system SHALL report which tool groups are currently enabled
4. WHEN no additional groups are enabled THEN the system SHALL report that only basic arithmetic is available

### Requirement 4

**User Story:** As a deployment engineer, I want to use predefined tool group combinations, so that I can quickly configure common use cases.

#### Acceptance Criteria

1. WHEN I set CALCULATOR_ENABLE_ALL=true THEN the system SHALL enable all 68 tools across all groups
2. WHEN I set CALCULATOR_ENABLE_SCIENTIFIC=true THEN the system SHALL enable basic, advanced, statistics, matrix, complex, and calculus groups
3. WHEN I set CALCULATOR_ENABLE_BUSINESS=true THEN the system SHALL enable basic, financial, currency, and units groups
4. WHEN I set CALCULATOR_ENABLE_ENGINEERING=true THEN the system SHALL enable basic, advanced, matrix, complex, calculus, units, and constants groups
5. WHEN multiple preset combinations are specified THEN the system SHALL enable the union of all specified tool groups

### Requirement 5

**User Story:** As a security administrator, I want to ensure that disabled tool groups cannot be accessed, so that I can maintain security boundaries in restricted environments.

#### Acceptance Criteria

1. WHEN a tool group is disabled THEN the system SHALL NOT register those tools with the MCP server
2. WHEN a disabled tool is called directly THEN the system SHALL return a "tool not found" error
3. WHEN the server starts THEN the system SHALL log which tool groups are enabled and disabled
4. WHEN tool group configuration changes THEN the system SHALL require a server restart to take effect
5. WHEN invalid environment variable values are provided THEN the system SHALL treat them as disabled and log a warning

### Requirement 6

**User Story:** As a developer, I want backward compatibility with existing deployments, so that current installations continue to work without configuration changes.

#### Acceptance Criteria

1. WHEN no tool group environment variables are set AND no legacy configuration exists THEN the system SHALL enable only basic arithmetic tools
2. WHEN the legacy CALCULATOR_ENABLE_ALL_TOOLS environment variable is set to true THEN the system SHALL enable all tool groups for backward compatibility
3. WHEN both legacy and new environment variables are present THEN the system SHALL prioritize the new group-specific variables
4. WHEN upgrading from a previous version THEN the system SHALL provide clear documentation on migration to the new environment variables