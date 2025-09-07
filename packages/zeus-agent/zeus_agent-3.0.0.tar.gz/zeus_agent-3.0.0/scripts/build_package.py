#!/usr/bin/env python3
"""
Zeus AI Platform Package Builder
用于构建和发布 Zeus 平台的 pip 包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """运行命令并返回结果"""
    print(f"🔧 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"⚠️ Stderr: {result.stderr}")
        
    if check and result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
        
    return result

def clean_build_artifacts():
    """清理构建产物"""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = [
        "build/",
        "dist/", 
        "*.egg-info/",
        "__pycache__/",
        "zeus/__pycache__/",
        "layers/__pycache__/",
        "lib/__pycache__/",
    ]
    
    for pattern in artifacts:
        if '*' in pattern:
            import glob
            for path in glob.glob(pattern, recursive=True):
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    print(f"   Removed: {path}")
        else:
            if os.path.exists(pattern):
                if os.path.isdir(pattern):
                    shutil.rmtree(pattern)
                else:
                    os.remove(pattern)
                print(f"   Removed: {pattern}")

def validate_package_structure():
    """验证包结构"""
    print("✅ Validating package structure...")
    
    required_files = [
        "setup.py",
        "pyproject.toml", 
        "MANIFEST.in",
        "README.md",
        "LICENSE",
        "requirements.txt",
        "__init__.py",
        "layers/__init__.py",
        "zeus/__init__.py",
        "zeus/cli.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        sys.exit(1)
    
    print("✅ Package structure validation passed")

def run_tests():
    """运行测试"""
    print("🧪 Running tests...")
    
    if not os.path.exists("tests/"):
        print("⚠️ No tests directory found, skipping tests")
        return
        
    try:
        run_command(["python", "-m", "pytest", "tests/", "-v", "--tb=short"])
        print("✅ All tests passed")
    except:
        print("⚠️ Some tests failed, but continuing with build")

def build_package():
    """构建包"""
    print("📦 Building package...")
    
    # Install build dependencies
    run_command([sys.executable, "-m", "pip", "install", "build", "twine"])
    
    # Build the package
    run_command([sys.executable, "-m", "build"])
    
    print("✅ Package built successfully")
    
    # List built files
    if os.path.exists("dist/"):
        print("📁 Built files:")
        for file in os.listdir("dist/"):
            print(f"   - dist/{file}")

def check_package():
    """检查构建的包"""
    print("🔍 Checking built package...")
    
    if not os.path.exists("dist/"):
        print("❌ No dist/ directory found")
        return
        
    # Find the wheel file
    wheel_files = [f for f in os.listdir("dist/") if f.endswith(".whl")]
    if not wheel_files:
        print("❌ No wheel file found")
        return
        
    wheel_file = f"dist/{wheel_files[0]}"
    
    # Check with twine
    run_command(["python", "-m", "twine", "check", "dist/*"])
    
    print("✅ Package check passed")

def install_locally():
    """本地安装测试"""
    print("🔧 Installing package locally for testing...")
    
    # Uninstall if already installed
    run_command([sys.executable, "-m", "pip", "uninstall", "zeus-ai-platform", "-y"], check=False)
    
    # Install from local build
    wheel_files = [f for f in os.listdir("dist/") if f.endswith(".whl")]
    if wheel_files:
        wheel_file = f"dist/{wheel_files[0]}"
        run_command([sys.executable, "-m", "pip", "install", wheel_file])
    else:
        run_command([sys.executable, "-m", "pip", "install", "."])
    
    print("✅ Local installation completed")

def test_installation():
    """测试安装"""
    print("🧪 Testing installation...")
    
    # Test CLI commands
    commands = [
        ["zeus", "--version"],
        ["zeus-agent", "--help"],
        ["zeus-dev", "--help"],
    ]
    
    for cmd in commands:
        try:
            result = run_command(cmd, check=False)
            if result.returncode == 0:
                print(f"✅ Command '{' '.join(cmd)}' works")
            else:
                print(f"⚠️ Command '{' '.join(cmd)}' failed")
        except Exception as e:
            print(f"⚠️ Command '{' '.join(cmd)}' error: {e}")
    
    # Test Python imports
    try:
        result = run_command([
            sys.executable, "-c", 
            "import zeus; from zeus import UniversalAgent; print('✅ Import test passed')"
        ], check=False)
        if result.returncode != 0:
            print("⚠️ Import test failed")
    except Exception as e:
        print(f"⚠️ Import test error: {e}")

def publish_package(repository: str = "testpypi"):
    """发布包到 PyPI"""
    print(f"🚀 Publishing to {repository}...")
    
    if repository == "testpypi":
        repo_url = "https://test.pypi.org/legacy/"
    else:
        repo_url = "https://upload.pypi.org/legacy/"
    
    run_command([
        "python", "-m", "twine", "upload", 
        "--repository-url", repo_url,
        "dist/*"
    ])
    
    print(f"✅ Package published to {repository}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Zeus AI Platform Package Builder")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--build", action="store_true", help="Build package")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--check", action="store_true", help="Check built package")
    parser.add_argument("--install", action="store_true", help="Install locally")
    parser.add_argument("--test-install", action="store_true", help="Test installation")
    parser.add_argument("--publish", choices=["testpypi", "pypi"], help="Publish to repository")
    parser.add_argument("--all", action="store_true", help="Run complete build pipeline")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🚀 Zeus AI Platform Package Builder")
    print("=" * 50)
    
    try:
        if args.clean or args.all:
            clean_build_artifacts()
            
        if args.all:
            validate_package_structure()
            
        if args.test or args.all:
            run_tests()
            
        if args.build or args.all:
            build_package()
            
        if args.check or args.all:
            check_package()
            
        if args.install or args.all:
            install_locally()
            
        if args.test_install or args.all:
            test_installation()
            
        if args.publish:
            publish_package(args.publish)
            
        print("🎉 Build pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
