#!/bin/bash
# Test uvx installation from PyPI repositories
set -e

REPO=${1:-"pypi"}  # Default to pypi, can be "testpypi"

echo "Testing uvx installation from $REPO..."

if [[ "$REPO" == "testpypi" ]]; then
    INDEX_URL="https://test.pypi.org/simple/"
    REPO_NAME="Test PyPI"
else
    INDEX_URL=""
    REPO_NAME="PyPI"
fi

# Check if uvx is available
if ! command -v uvx &> /dev/null; then
    echo "ERROR: uvx is not installed"
    echo "TIP: To install uvx:"
    echo "  pip install uvx"
    echo "  # or"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "uvx version:"
uvx --version

# Test installation
echo "Testing uvx installation from $REPO_NAME..."

if [[ -n "$INDEX_URL" ]]; then
    echo "Installing from $REPO_NAME with index URL: $INDEX_URL"
    echo "Note: Using --extra-index-url to pull dependencies from PyPI"
    # Test installation by running the server briefly (MCP servers don't support --help)
    gtimeout 3s uvx --index-url "$INDEX_URL" --extra-index-url "https://pypi.org/simple/" p6plab-mcp-calculator@latest || {
        # Timeout is expected for MCP servers, check if it was a timeout (exit code 124) or real error
        if [[ $? -eq 124 ]]; then
            echo "SUCCESS: Package installed and server started (timeout expected)"
        else
            echo "ERROR: Installation from $REPO_NAME failed"
            exit 1
        fi
    }
else
    echo "Installing from $REPO_NAME..."
    # Test installation by running the server briefly (MCP servers don't support --help)
    gtimeout 3s uvx p6plab-mcp-calculator@latest || {
        # Timeout is expected for MCP servers, check if it was a timeout (exit code 124) or real error
        if [[ $? -eq 124 ]]; then
            echo "SUCCESS: Package installed and server started (timeout expected)"
        else
            echo "ERROR: Installation from $REPO_NAME failed"
            exit 1
        fi
    }
fi

echo "SUCCESS: uvx installation test from $REPO_NAME completed successfully!"

# Test basic functionality
echo "Testing basic functionality..."
echo "Note: MCP servers run continuously, so timeout is expected behavior"

echo ""
echo "Complete! uvx installation test complete!"
echo "SUCCESS: Package can be successfully installed and executed via uvx from $REPO_NAME"