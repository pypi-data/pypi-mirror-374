<!------------------------------------------------------------------------------------
   Add Rules to this file or a short description and have Kiro refine them for you:   
-------------------------------------------------------------------------------------> 
# KIRO Steering Document: Scientific Calculator MCP Server

## Project Overview

**Project Name:** Scientific Calculator MCP Server  
**Project Type:** Model Context Protocol (MCP) Server Development  
**Target Audience:** AI assistants and developers requiring mathematical computation capabilities

## Key Results (KRs)

### KR1: Core Mathematical Engine
**Objective:** Deliver a robust mathematical computation foundation
- **Metric:** 100% test coverage for basic arithmetic operations
- **Metric:** Support for 20+ advanced mathematical functions (trigonometric, logarithmic, exponential)
- **Metric:** Statistical operations covering descriptive stats and 5+ probability distributions
- **Success Criteria:** All basic and advanced mathematical operations respond within performance requirements (<100ms)

### KR2: Advanced Computational Features
**Objective:** Implement sophisticated mathematical capabilities
- **Metric:** Complete matrix operations library (multiplication, determinant, inverse, eigenvalues)
- **Metric:** Symbolic calculus operations (derivatives, integrals) using SymPy
- **Metric:** Equation solving for linear, quadratic, and polynomial equations
- **Success Criteria:** Matrix operations handle up to 100x100 matrices within 1 second

### KR3: Practical Applications & Integrations
**Objective:** Provide real-world utility through conversions and specialized calculations
- **Metric:** Unit conversion system supporting 10+ unit types (length, weight, temperature, etc.)
- **Metric:** Optional currency conversion with 3 fallback mechanisms (API key, free tier, cached rates)
- **Metric:** Financial calculation tools (compound interest, NPV, IRR)
- **Success Criteria:** Unit conversions achieve 100% accuracy, currency conversion disabled by default

### KR4: Production Readiness
**Objective:** Deliver a production-ready, secure, and well-documented MCP server
- **Metric:** 95%+ test coverage across all modules
- **Metric:** Complete API documentation with usage examples
- **Metric:** Security audit with input validation and resource limits
- **Metric:** Performance benchmarks meeting all response time requirements
- **Success Criteria:** Package ready for PyPI and Test PyPI distribution with uvx execution support and comprehensive documentation

## Initiatives

### Initiative 1: MCP Framework Integration
**Owner:** Lead Developer  
**Timeline:** Week 1  
**Description:** Establish FastMCP server foundation following AWS MCP server patterns
- Use latest version of FastMCP v2 library (https://github.com/jlowin/fastmcp) for MCP framework implementation
- Set up project structure mirroring AWS MCP server architecture
- Implement Pydantic models for request/response validation
- Configure logging with loguru
- Establish error handling framework

### Initiative 2: Mathematical Core Development
**Owner:** Lead Developer  
**Timeline:** Weeks 2-3  
**Description:** Build comprehensive mathematical computation engine
- Implement numpy/scipy integration for numerical operations
- Add SymPy for symbolic mathematics
- Create precision handling with decimal module
- Develop statistical analysis capabilities

### Initiative 3: Advanced Features Implementation
**Owner:** Lead Developer  
**Timeline:** Weeks 4-5  
**Description:** Add sophisticated mathematical capabilities
- Matrix operations and linear algebra
- Calculus operations (derivatives, integrals)
- Equation solving algorithms
- Optimization functions

### Initiative 4: Practical Applications
**Owner:** Lead Developer  
**Timeline:** Week 6  
**Description:** Implement real-world utility features
- Unit conversion system with comprehensive coverage
- Optional currency conversion with privacy controls
- Financial calculation tools
- Physics/chemistry specialized functions

### Initiative 5: Quality Assurance & Documentation
**Owner:** Lead Developer  
**Timeline:** Weeks 7-8  
**Description:** Ensure production readiness
- Comprehensive testing strategy (unit, integration, performance)
- Complete API documentation
- Security audit and validation
- Performance optimization and benchmarking
- PyPI packaging with uvx execution support
- Test PyPI validation and final PyPI publication

## Risks & Mitigation

### High Risk: Performance with Large Calculations
**Risk:** Matrix operations and complex calculations may exceed response time requirements
**Mitigation:** 
- Implement caching for expensive operations
- Add computation limits and timeouts
- Use optimized libraries (numpy, scipy)
- Performance testing in Phase 7

### Medium Risk: External API Dependency (Currency)
**Risk:** Currency conversion API reliability and rate limits
**Mitigation:**
- Feature disabled by default
- Multiple fallback mechanisms (API key → free tier → cached rates)
- Graceful degradation when API unavailable
- Clear user control via environment variables

### Medium Risk: Security Vulnerabilities
**Risk:** Mathematical expression evaluation could allow code injection
**Mitigation:**
- Strict input validation using Pydantic
- No use of eval() for expression parsing
- Use SymPy for safe symbolic math parsing
- Comprehensive security audit in Phase 8

### Low Risk: Dependency Management
**Risk:** Complex scientific computing dependencies may cause installation issues
**Mitigation:**
- Use well-established libraries (numpy, scipy, sympy)
- Comprehensive dependency testing
- Clear installation documentation
- Support for multiple installation methods (pip, uvx)

## Success Metrics

### Technical Metrics
- **Test Coverage:** ≥95% across all modules
- **Performance:** All operations meet specified response times
- **Accuracy:** Mathematical operations maintain 15 decimal places precision
- **Reliability:** 99.9% uptime for local operations

### User Experience Metrics
- **Installation Success Rate:** ≥95% successful installations via pip and uvx
- **Documentation Completeness:** All tools documented with examples including uvx usage
- **Error Handling:** Clear error messages with actionable suggestions
- **Security:** Zero security vulnerabilities in audit
- **PyPI Readiness:** Successfully published to Test PyPI and ready for PyPI publication

### Business Metrics
- **Feature Completeness:** All 8 phases delivered on schedule
- **Code Quality:** Passes all linting and type checking (ruff, pyright)
- **Distribution Ready:** Package available on PyPI and Test PyPI with uvx execution support
- **Community Adoption:** Ready for integration with MCP clients via pip install and uvx execution

## Development Standards

### Code Quality
- **Linting:** ruff with line length 99 characters
- **Type Checking:** pyright for static type analysis
- **Testing:** pytest with asyncio support
- **Documentation:** Google-style docstrings
- **Formatting:** ruff formatter with single quotes
- **Environment:** Python virtual environments (venv) required for development and testing
- **MCP Framework:** Use latest version of FastMCP v2 library (https://github.com/jlowin/fastmcp)
- **Code Style:** No emojis in code, comments, or shell scripts - use plain text for professional appearance

### Security Standards
- **Input Validation:** All inputs validated with Pydantic
- **Resource Limits:** Computation time and memory limits
- **External APIs:** Disabled by default, explicit user enablement required
- **Error Handling:** No sensitive information in error messages

### Performance Standards
- **Response Times:** As specified in p6plab-mcp-calculator.md
- **Memory Usage:** Efficient handling of large datasets
- **Caching:** Expensive operations cached appropriately
- **Concurrency:** Support for concurrent operations

## Stakeholder Communication

### Weekly Status Updates
- **Format:** Progress against KRs and current phase deliverables
- **Audience:** Project stakeholders
- **Content:** Completed features, blockers, next week priorities

### Phase Gate Reviews
- **Format:** Formal review of phase deliverables
- **Audience:** Technical reviewers, stakeholders
- **Content:** Demo of functionality, test results, quality metrics

### Final Delivery Review
- **Format:** Comprehensive project review
- **Audience:** All stakeholders
- **Content:** Complete feature demonstration, performance benchmarks, documentation review