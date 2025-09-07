#!/bin/bash
# Build uvx-compatible package for distribution
set -e

echo "Building uvx-compatible package..."

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Warning: Not in a virtual environment. Activating venv..."
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
    else
        echo "ERROR: Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate"
        exit 1
    fi
fi

# Install build dependencies if not present
echo "Installing build dependencies..."
pip install --upgrade build twine

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build the package
echo "Building wheel and source distribution..."
python -m build --wheel --sdist

echo "Package built successfully"

# Validate uvx compatibility
echo "Validating uvx compatibility..."

# Check entry points
echo "Entry points:"
python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)
    scripts = config.get('project', {}).get('scripts', {})
    if scripts:
        for name, entry in scripts.items():
            print(f'  {name} = {entry}')
    else:
        print('  No entry points found!')
        exit(1)
"

# Check dependencies
echo "Dependencies:"
python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)
    deps = config.get('project', {}).get('dependencies', [])
    for dep in deps:
        print(f'  {dep}')
"

echo "uvx compatibility validated"
echo "Package files created in dist/:"
ls -la dist/

echo ""
echo "Build complete! You can now:"
echo "  - Test locally: ./scripts/test-uvx-package.sh"
echo "  - Publish to Test PyPI: ./scripts/publish-test-pypi.sh"
echo "  - Publish to PyPI: ./scripts/publish-pypi.sh"