#!/bin/bash
# Local PyPI publishing script for fdprof
set -e

echo "🚀 fdprof Local Publishing Script"
echo "================================="

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo "❌ Error: Must run from fdprof project root directory"
    exit 1
fi

# Get current version
CURRENT_VERSION=$(uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
echo "📦 Current version: $CURRENT_VERSION"

# Prompt for confirmation
echo
read -p "🤔 Publish version $CURRENT_VERSION to PyPI? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Publishing cancelled"
    exit 0
fi

echo "🧹 Cleaning previous builds..."
rm -rf dist/

echo "🏗️  Building package..."
uv build

echo "✅ Validating package..."
uv run twine check dist/*

echo "📋 Package contents:"
ls -la dist/
echo
echo "📦 Wheel contents:"
unzip -l dist/*.whl

echo
read -p "🧪 Test upload to TestPyPI first? (Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo "📤 Uploading to TestPyPI..."
    uv run twine upload --repository testpypi dist/*

    echo "✅ TestPyPI upload complete!"
    echo "🔍 Test installation: pip install --index-url https://test.pypi.org/simple/ fdprof==$CURRENT_VERSION"
    echo
    read -p "📦 Continue with production PyPI upload? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Production upload cancelled"
        exit 0
    fi
fi

echo "📤 Uploading to production PyPI..."
uv run twine upload dist/*

echo
echo "🎉 Success! fdprof $CURRENT_VERSION published to PyPI"
echo "🔍 Test installation: pip install fdprof==$CURRENT_VERSION"
echo "🌐 PyPI page: https://pypi.org/project/fdprof/"
