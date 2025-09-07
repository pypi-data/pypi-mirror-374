#!/bin/bash
# Publish to Test PyPI
set -e

echo "Publishing to Test PyPI..."

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "WARNING: Not in a virtual environment. Activating venv..."
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    else
        echo "ERROR: Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate"
        exit 1
    fi
fi

# Check if package is built
if [[ ! -d "dist" ]] || [[ -z "$(ls -A dist/)" ]]; then
    echo "ERROR: No package files found in dist/"
    echo "TIP: Run ./scripts/build-uvx-package.sh first"
    exit 1
fi

# Install twine if not present
echo "Ensuring twine is installed..."
pip install --upgrade twine

# Check credentials
echo "Checking Test PyPI credentials..."
if [[ -z "$TWINE_USERNAME" ]] && [[ -z "$TWINE_PASSWORD" ]]; then
    echo "WARNING: No credentials found in environment variables"
    echo "TIP: You can set credentials with:"
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=your-test-pypi-token"
    echo ""
    echo "Or configure them interactively when prompted"
fi

# Upload to Test PyPI
echo "Uploading to Test PyPI..."
python -m twine upload --repository testpypi dist/* || {
    echo "ERROR: Upload to Test PyPI failed"
    echo "TIP: Common issues:"
    echo "  - Package version already exists (update version in calculator/__init__.py)"
    echo "  - Invalid credentials (check TWINE_USERNAME and TWINE_PASSWORD)"
    echo "  - Network issues (check internet connection)"
    exit 1
}

echo "SUCCESS: Published to Test PyPI successfully!"

# Wait a moment for the package to be available
echo "Waiting for package to be available on Test PyPI..."
sleep 10

# Test installation from Test PyPI
echo "Testing installation from Test PyPI..."
./scripts/test-uvx-install.sh testpypi || {
    echo "WARNING: Installation test failed, but package was uploaded"
    echo "TIP: The package might need a few minutes to be fully available"
}

echo ""
echo "Complete! Test PyPI publication complete!"
echo "Link: Check your package at: https://test.pypi.org/project/p6plab-mcp-calculator/"
echo ""
echo "SUCCESS: Next steps:"
echo "  - Verify the package page on Test PyPI"
echo "  - Test installation: uvx --index-url https://test.pypi.org/simple/ p6plab-mcp-calculator@latest"
echo "  - If everything looks good, publish to production: ./scripts/publish-pypi.sh"