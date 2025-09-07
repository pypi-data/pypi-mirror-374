#!/bin/bash
# Zeus AI Platform Quick Build Script
# 快速构建和测试 Zeus 平台包

echo "🚀 Zeus AI Platform Quick Build"
echo "================================"

# 确保在正确的目录
if [ ! -f "setup.py" ]; then
    echo "❌ setup.py not found. Please run from project root directory."
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# 安装构建依赖
echo "📦 Installing build dependencies..."
pip install --upgrade pip build twine

# 清理旧的构建产物
echo "🧹 Cleaning old build artifacts..."
rm -rf build/ dist/ *.egg-info/

# 构建包
echo "🏗️ Building package..."
python -m build

# 检查构建的包
echo "🔍 Checking built package..."
python -m twine check dist/*

# 列出构建的文件
echo "📁 Built files:"
ls -la dist/

echo "✅ Quick build completed!"
echo ""
echo "📋 Next steps:"
echo "   • Test install: pip install dist/*.whl"
echo "   • Test CLI: zeus --version"
echo "   • Publish to test PyPI: python scripts/build_package.py --publish testpypi"
echo "   • Publish to PyPI: python scripts/build_package.py --publish pypi"
