# Scientific Calculator MCP Server - Release Guide

This document provides comprehensive instructions for releasing the Scientific Calculator MCP Server to PyPI using the provided shell scripts.

## Prerequisites

Before releasing, ensure you have:

1. **Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Build Tools**
   ```bash
   pip install build twine
   ```

3. **uvx (for testing)**
   ```bash
   pip install uvx
   # or
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **PyPI Credentials**
   - Create accounts on [PyPI](https://pypi.org) and [Test PyPI](https://test.pypi.org)
   - Generate API tokens for both repositories
   - Configure credentials in `~/.pypirc`:
   ```ini
   [distutils]
   index-servers = pypi testpypi

   [pypi]
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-your-test-api-token-here
   ```

## Release Workflow

### Step 1: Pre-Release Validation

1. **Run Tests**
   ```bash
   ./scripts/run-tests.sh
   ```

2. **Clean Previous Builds**
   ```bash
   ./scripts/clean.sh
   ```

3. **Build uvx Package**
   ```bash
   ./scripts/build-uvx-package.sh
   ```

4. **Test Local uvx Package**
   ```bash
   ./scripts/test-uvx-package.sh
   ```

### Step 2: Test PyPI Release

1. **Publish to Test PyPI**
   ```bash
   ./scripts/publish-test-pypi.sh
   ```

2. **Test Installation from Test PyPI**
   ```bash
   ./scripts/test-uvx-install.sh testpypi
   ```

3. **Validate Package Metadata**
   - Visit https://test.pypi.org/project/p6plab-mcp-calculator/
   - Verify package description, metadata, and dependencies
   - Check that uvx installation works correctly

### Step 3: Production PyPI Release

1. **Final Validation**
   - Ensure all tests pass
   - Verify version number in `pyproject.toml`
   - Confirm changelog is updated
   - Review package metadata

2. **Publish to Production PyPI**
   ```bash
   ./scripts/publish-pypi.sh
   ```
   
   **⚠️ Warning**: This publishes to production PyPI and cannot be undone!

3. **Test Production Installation**
   ```bash
   ./scripts/test-uvx-install.sh pypi
   ```

4. **Verify Production Package**
   - Visit https://pypi.org/project/p6plab-mcp-calculator/
   - Test installation: `uvx p6plab-mcp-calculator@latest`
   - Verify all functionality works correctly

## Shell Scripts Reference

### `scripts/build-uvx-package.sh`
Builds the package with uvx compatibility:
- Creates wheel and source distributions
- Validates entry points
- Checks uvx compatibility

### `scripts/test-uvx-package.sh`
Tests the package locally:
- Installs package in development mode
- Tests uvx execution
- Validates basic functionality

### `scripts/publish-test-pypi.sh`
Publishes to Test PyPI:
- Uploads package to test.pypi.org
- Tests installation from Test PyPI
- Validates uvx execution from Test PyPI

### `scripts/publish-pypi.sh`
Publishes to production PyPI:
- **Requires confirmation** before publishing
- Uploads to pypi.org
- Tests installation from production PyPI
- Validates uvx execution

### `scripts/test-uvx-install.sh`
Tests uvx installation from PyPI repositories:
```bash
# Test from Test PyPI
./scripts/test-uvx-install.sh testpypi

# Test from production PyPI
./scripts/test-uvx-install.sh pypi
```

### `scripts/run-tests.sh`
Runs comprehensive test suite:
- Unit tests
- Integration tests
- Coverage reporting

### `scripts/clean.sh`
Cleans build artifacts:
- Removes dist/ directory
- Cleans Python cache files
- Removes temporary files

## Version Management

### Semantic Versioning
Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Update Process
1. Update version in `pyproject.toml`:
   ```toml
   [project]
   version = "1.2.3"
   ```

2. Update changelog in `CHANGELOG.md`

3. Commit version changes:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 1.2.3"
   git tag v1.2.3
   git push origin main --tags
   ```

## Automated PyPI Deployment Pipeline

### GitHub Actions (Recommended)
Create `.github/workflows/release.yml`:

```yaml
name: Release to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Run tests
      run: ./scripts/run-tests.sh
    
    - name: Build package
      run: ./scripts/build-uvx-package.sh
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        python -m twine upload dist/*
    
    - name: Test uvx installation
      run: ./scripts/test-uvx-install.sh pypi
```

### Manual Release Checklist

- [ ] All tests pass (`./scripts/run-tests.sh`)
- [ ] Version updated in `pyproject.toml`
- [ ] Changelog updated
- [ ] Clean build (`./scripts/clean.sh`)
- [ ] Build package (`./scripts/build-uvx-package.sh`)
- [ ] Test local package (`./scripts/test-uvx-package.sh`)
- [ ] Publish to Test PyPI (`./scripts/publish-test-pypi.sh`)
- [ ] Test Test PyPI installation (`./scripts/test-uvx-install.sh testpypi`)
- [ ] Publish to PyPI (`./scripts/publish-pypi.sh`)
- [ ] Test PyPI installation (`./scripts/test-uvx-install.sh pypi`)
- [ ] Create GitHub release
- [ ] Update documentation

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify PyPI API tokens are correct
   - Check `~/.pypirc` configuration
   - Ensure tokens have upload permissions

2. **Package Already Exists**
   - PyPI doesn't allow overwriting versions
   - Increment version number and retry

3. **uvx Installation Fails**
   - Check package dependencies
   - Verify entry points in `pyproject.toml`
   - Test with `pip install` first

4. **Build Failures**
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify `pyproject.toml` syntax

### Getting Help

- Check the [troubleshooting guide](troubleshooting.md)
- Review PyPI documentation
- Check uvx documentation
- Open an issue on the project repository

## Security Considerations

1. **API Token Security**
   - Never commit API tokens to version control
   - Use environment variables or secure credential storage
   - Rotate tokens regularly

2. **Package Integrity**
   - Always test packages before releasing
   - Use Test PyPI for validation
   - Verify package contents match expectations

3. **Version Control**
   - Tag releases in git
   - Maintain changelog
   - Use signed commits for releases

## Post-Release Tasks

1. **Update Documentation**
   - Update installation instructions
   - Refresh usage examples
   - Update version references

2. **Announce Release**
   - Create GitHub release notes
   - Update project README
   - Notify users of new features

3. **Monitor**
   - Check PyPI download statistics
   - Monitor for user feedback
   - Watch for bug reports

---

**Note**: This release process ensures the Scientific Calculator MCP Server can be reliably distributed via PyPI and executed using uvx, providing users with a seamless installation and execution experience.