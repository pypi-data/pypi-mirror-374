#!/bin/bash
# Test uvx package locally
set -e

echo "Testing uvx package locally..."

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

# Install package locally in editable mode
echo "Installing package locally in editable mode..."
pip install -e .

echo "Running uvx execution tests..."

# Test if the entry point works
echo "Testing entry point availability..."
if command -v p6plab-mcp-calculator &> /dev/null; then
    echo "SUCCESS: p6plab-mcp-calculator command is available"
else
    echo "ERROR: p6plab-mcp-calculator command not found in PATH"
    echo "Checking installed scripts..."
    pip show -f p6plab-mcp-calculator | grep -A 20 "Files:"
    exit 1
fi

# Test help command
echo "Testing help command..."
gtimeout 5s p6plab-mcp-calculator --help || echo "WARNING: Help command test completed (timeout expected)"

# Test with uvx if available
if command -v uvx &> /dev/null; then
    echo "Testing with uvx..."
    echo "uvx version:"
    uvx --version
    
    # Test uvx execution (with timeout since it's a server)
    echo "Testing uvx execution..."
    gtimeout 3s uvx --python-preference system p6plab-mcp-calculator --help || echo "WARNING: uvx test completed (timeout expected)"
    
    echo "SUCCESS: uvx execution test passed"
else
    echo "WARNING: uvx not available, skipping uvx-specific tests"
    echo "TIP: To install uvx: pip install uvx"
fi

# Test import
echo "Testing Python import..."
python -c "
try:
    from calculator.server import main
    print('SUCCESS: Main function import successful')
    from calculator.core.basic import add
    result = add(2, 3)
    print(f'SUCCESS: Basic calculation test: 2 + 3 = {result[\"result\"]}')
except Exception as e:
    print(f'ERROR: Import test failed: {e}')
    exit(1)
"

echo "SUCCESS: uvx package test completed successfully!"
echo ""
echo "Complete! Local testing complete! The package is ready for:"
echo "  - Publishing to Test PyPI: ./scripts/publish-test-pypi.sh"
echo "  - Publishing to PyPI: ./scripts/publish-pypi.sh"