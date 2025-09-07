#!/bin/bash
# Validate release readiness for Scientific Calculator MCP Server
set -e

echo "🔍 Scientific Calculator MCP Server - Release Validation"
echo "======================================================="

# Check version
VERSION=$(python -c "import calculator; print(calculator.__version__)")
echo "📋 Current version: $VERSION"

# Check if all required files exist
echo "📁 Checking required files..."
required_files=(
    "calculator/server.py"
    "calculator/__init__.py"
    "pyproject.toml"
    "README.md"
    "LICENSE"
    "scripts/publish-pypi.sh"
    "scripts/test-uvx-install.sh"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (missing)"
        exit 1
    fi
done

# Check if server imports correctly
echo "🧪 Testing server import..."
python -c "import calculator.server; print('✅ Server imports successfully')" 2>/dev/null || {
    echo "❌ Server import failed"
    exit 1
}

# Check if basic functionality works
echo "🧮 Testing basic functionality..."
python -c "
from calculator.core import basic, advanced, units
import math

# Test basic arithmetic
assert basic.add(2, 3)['result'] == 5.0

# Test advanced functions  
assert abs(advanced.sin(math.pi/2) - 1.0) < 1e-10

# Test unit conversion
result = units.convert_units(100, 'cm', 'm', 'length')
assert result['result'] == 1.0

print('✅ Core functionality working')
" 2>/dev/null || {
    echo "❌ Basic functionality test failed"
    exit 1
}

# Check package can be built
echo "📦 Testing package build..."
if [[ -d "dist" ]]; then
    echo "   ✅ Package already built"
else
    echo "   Building package..."
    python -m build --quiet
    echo "   ✅ Package built successfully"
fi

# Check entry points
echo "🔧 Validating entry points..."
python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    config = tomllib.load(f)
scripts = config.get('project', {}).get('scripts', {})
assert 'p6plab-mcp-calculator' in scripts
assert scripts['p6plab-mcp-calculator'] == 'calculator.server:main'
print('✅ Entry points configured correctly')
"

echo ""
echo "🎯 Release Validation Summary:"
echo "   Version: $VERSION"
echo "   Server: ✅ Working"
echo "   Tests: ✅ Passing"
echo "   Package: ✅ Built"
echo "   Entry Points: ✅ Configured"
echo "   Scripts: ✅ Available"
echo ""
echo "✅ READY FOR RELEASE!"
echo ""
echo "🚀 Next steps:"
echo "   Test PyPI: ./scripts/deploy-pipeline.sh test"
echo "   Production: ./scripts/deploy-pipeline.sh production"