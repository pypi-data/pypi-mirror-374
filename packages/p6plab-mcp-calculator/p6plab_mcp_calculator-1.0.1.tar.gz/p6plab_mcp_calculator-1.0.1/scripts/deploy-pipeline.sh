#!/bin/bash
# Complete deployment pipeline for Scientific Calculator MCP Server
set -e

STAGE=${1:-"test"}  # test, production

echo "🚀 Scientific Calculator MCP Server Deployment Pipeline"
echo "======================================================="
echo "Stage: $STAGE"
echo ""

# Step 1: Pre-deployment validation
echo "📋 Step 1: Pre-deployment validation"
echo "Running comprehensive tests..."
./scripts/run-tests.sh

echo "Cleaning previous builds..."
./scripts/clean.sh

echo "Building uvx package..."
./scripts/build-uvx-package.sh

echo "Testing local uvx package..."
./scripts/test-uvx-package.sh

echo "✅ Pre-deployment validation complete"
echo ""

# Step 2: Deploy based on stage
if [[ "$STAGE" == "test" ]]; then
    echo "📦 Step 2: Test PyPI Deployment"
    echo "Publishing to Test PyPI..."
    ./scripts/publish-test-pypi.sh
    
    echo "Testing installation from Test PyPI..."
    ./scripts/test-uvx-install.sh testpypi
    
    echo "✅ Test PyPI deployment complete"
    echo ""
    echo "🎉 SUCCESS: Package successfully deployed to Test PyPI!"
    echo "   Visit: https://test.pypi.org/project/p6plab-mcp-calculator/"
    echo "   Test: uvx --index-url https://test.pypi.org/simple/ p6plab-mcp-calculator@latest"
    
elif [[ "$STAGE" == "production" ]]; then
    echo "🚨 Step 2: Production PyPI Deployment"
    echo "WARNING: This will deploy to production PyPI!"
    echo ""
    
    # Final confirmation
    read -p "Are you sure you want to deploy to production PyPI? (yes/NO): " confirm
    if [[ $confirm != "yes" ]]; then
        echo "❌ Production deployment cancelled"
        exit 0
    fi
    
    echo "Publishing to production PyPI..."
    ./scripts/publish-pypi.sh
    
    echo "Testing installation from production PyPI..."
    ./scripts/test-uvx-install.sh pypi
    
    echo "✅ Production PyPI deployment complete"
    echo ""
    echo "🎉 SUCCESS: Package successfully deployed to production PyPI!"
    echo "   Visit: https://pypi.org/project/p6plab-mcp-calculator/"
    echo "   Install: uvx p6plab-mcp-calculator@latest"
    
else
    echo "❌ ERROR: Invalid stage '$STAGE'. Use 'test' or 'production'"
    exit 1
fi

echo ""
echo "📊 Deployment Summary:"
echo "   Stage: $STAGE"
echo "   Version: $(python -c 'import calculator; print(calculator.__version__)')"
echo "   Status: ✅ SUCCESS"
echo ""
echo "🔗 Next Steps:"
if [[ "$STAGE" == "test" ]]; then
    echo "   1. Test the package thoroughly on Test PyPI"
    echo "   2. If everything works, run: ./scripts/deploy-pipeline.sh production"
else
    echo "   1. Update documentation with new version"
    echo "   2. Create GitHub release notes"
    echo "   3. Announce the release"
fi

echo ""
echo "🎯 Deployment pipeline complete!"