#!/bin/bash
# Update version for Scientific Calculator MCP Server
set -e

VERSION_TYPE=${1:-"patch"}  # patch, minor, major
CURRENT_VERSION=$(python3 -c "import calculator; print(calculator.__version__)")

echo "Current version: $CURRENT_VERSION"

# Parse current version
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Calculate new version
case $VERSION_TYPE in
    "major")
        NEW_MAJOR=$((MAJOR + 1))
        NEW_MINOR=0
        NEW_PATCH=0
        ;;
    "minor")
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$((MINOR + 1))
        NEW_PATCH=0
        ;;
    "patch")
        NEW_MAJOR=$MAJOR
        NEW_MINOR=$MINOR
        NEW_PATCH=$((PATCH + 1))
        ;;
    *)
        echo "ERROR: Invalid version type. Use 'major', 'minor', or 'patch'"
        exit 1
        ;;
esac

NEW_VERSION="$NEW_MAJOR.$NEW_MINOR.$NEW_PATCH"

echo "New version: $NEW_VERSION"

# Confirm with user
read -p "Update version from $CURRENT_VERSION to $NEW_VERSION? (y/N): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Version update cancelled"
    exit 0
fi

# Update version in calculator/__init__.py
sed -i.bak "s/__version__ = \"$CURRENT_VERSION\"/__version__ = \"$NEW_VERSION\"/" calculator/__init__.py
rm calculator/__init__.py.bak

echo "Version updated to $NEW_VERSION"

# Offer to create git tag
read -p "Create git tag v$NEW_VERSION? (y/N): " create_tag
if [[ $create_tag == [yY] ]]; then
    git add calculator/__init__.py
    git commit -m "Bump version to $NEW_VERSION"
    git tag "v$NEW_VERSION"
    echo "Git tag v$NEW_VERSION created"
    echo "Don't forget to push: git push origin main --tags"
fi

echo "Version update complete!"