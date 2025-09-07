#!/bin/bash
# Publish to production PyPI
set -e

echo "WARNING: Publishing to production PyPI..."
echo "ALERT: This will make the package publicly available on PyPI!"
echo ""

# Confirmation prompt
read -p "Are you sure you want to publish to production PyPI? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "ERROR: Publication cancelled"
    exit 1
fi

echo ""
read -p "Have you tested the package on Test PyPI? (y/N): " tested
if [[ $tested != [yY] ]]; then
    echo "WARNING: Please test on Test PyPI first: ./scripts/publish-test-pypi.sh"
    exit 1
fi

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
echo "Checking PyPI credentials..."
if [[ -z "$TWINE_USERNAME" ]] && [[ -z "$TWINE_PASSWORD" ]]; then
    echo "WARNING: No credentials found in environment variables"
    echo "TIP: You can set credentials with:"
    echo "  export TWINE_USERNAME=__token__"
    echo "  export TWINE_PASSWORD=your-pypi-token"
    echo ""
    echo "Or configure them interactively when prompted"
fi

# Final confirmation
echo ""
echo "ALERT: FINAL CONFIRMATION"
echo "This will publish p6plab-mcp-calculator to production PyPI"
echo "The package will be publicly available and cannot be deleted"
echo ""
read -p "Type 'PUBLISH' to confirm: " final_confirm
if [[ $final_confirm != "PUBLISH" ]]; then
    echo "ERROR: Publication cancelled"
    exit 1
fi

# Upload to PyPI
echo ""
echo "Uploading to production PyPI..."
python -m twine upload dist/* || {
    echo "ERROR: Upload to PyPI failed"
    echo "TIP: Common issues:"
    echo "  - Package version already exists (update version in calculator/__init__.py)"
    echo "  - Invalid credentials (check TWINE_USERNAME and TWINE_PASSWORD)"
    echo "  - Network issues (check internet connection)"
    exit 1
}

echo "SUCCESS: Published to production PyPI successfully!"

# Wait a moment for the package to be available
echo "Waiting for package to be available on PyPI..."
sleep 15

# Test installation from PyPI
echo "Testing installation from PyPI..."
./scripts/test-uvx-install.sh pypi || {
    echo "WARNING: Installation test failed, but package was uploaded"
    echo "TIP: The package might need a few minutes to be fully available"
}

echo ""
echo "Complete! Production PyPI publication complete!"
echo "Link: Check your package at: https://pypi.org/project/p6plab-mcp-calculator/"
echo ""
echo "SUCCESS: Your package is now available to everyone:"
echo "  - Install with pip: pip install p6plab-mcp-calculator"
echo "  - Run with uvx: uvx p6plab-mcp-calculator@latest"
echo ""
echo "Congratulations! Congratulations on publishing your MCP server!"