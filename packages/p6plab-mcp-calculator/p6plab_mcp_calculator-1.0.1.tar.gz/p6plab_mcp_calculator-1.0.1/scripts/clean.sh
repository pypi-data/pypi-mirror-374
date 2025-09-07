#!/bin/bash
# Clean build artifacts and uvx cache
set -e

echo "Cleaning build artifacts and caches..."

# Clean Python build artifacts
echo "Removing Python build artifacts..."
rm -rf build/
rm -rf dist/
rm -rf test-dist/
rm -rf *.egg-info/
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# Clean test artifacts
echo "Removing test artifacts..."
rm -rf .pytest_cache/
rm -rf htmlcov/
rm -rf .coverage
rm -rf .coverage.*
rm -rf .tox/
rm -rf .mypy_cache/
rm -rf .ruff_cache/

# Clean documentation build artifacts
echo "Removing documentation artifacts..."
rm -rf docs/_build/

# Clean uvx cache (if uvx is available)
if command -v uvx &> /dev/null; then
    echo "Cleaning uvx cache..."
    # Note: uvx doesn't have a direct cache clean command, but we can remove the cache directory
    if [[ -d "$HOME/.cache/uv" ]]; then
        echo "Removing uv/uvx cache directory..."
        rm -rf "$HOME/.cache/uv"
    fi
    
    if [[ -d "$HOME/.local/share/uv" ]]; then
        echo "Removing uv/uvx data directory..."
        rm -rf "$HOME/.local/share/uv"
    fi
else
    echo "WARNING: uvx not available, skipping uvx cache cleanup"
fi

# Clean temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.temp" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

# Clean IDE files (optional)
echo "Removing IDE artifacts..."
rm -rf .vscode/settings.json 2>/dev/null || true
rm -rf .idea/ 2>/dev/null || true

# Show what's left
echo ""
echo "SUCCESS: Cleanup complete!"
echo ""
echo "Directory structure:"
find . -type f -not -path "./venv/*" -not -path "./.git/*" | head -20

if [[ $(find . -type f -not -path "./venv/*" -not -path "./.git/*" | wc -l) -gt 20 ]]; then
    echo "... (and more files)"
fi

echo ""
echo "Complete! All build artifacts and caches have been cleaned!"
echo ""
echo "TIP: You can now:"
echo "  - Run tests: ./scripts/run-tests.sh"
echo "  - Build package: ./scripts/build-uvx-package.sh"
echo "  - Start fresh development"