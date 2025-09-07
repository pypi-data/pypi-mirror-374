#!/usr/bin/env python3
"""
Zeus AI Platform PyPI Publisher
用于发布 Zeus 平台到 PyPI 的脚本
"""

import os
import sys
import subprocess
import getpass
from pathlib import Path
from typing import Optional

def run_command(cmd: list, check: bool = True) -> subprocess.CompletedProcess:
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

def check_prerequisites():
    """检查发布前提条件"""
    print("🔍 Checking prerequisites...")
    
    # 检查是否在正确的分支
    result = run_command(["git", "branch", "--show-current"])
    current_branch = result.stdout.strip()
    if current_branch != "release/v3.0.0":
        print(f"⚠️ Warning: You're on branch '{current_branch}', expected 'release/v3.0.0'")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # 检查工作目录是否干净
    result = run_command(["git", "status", "--porcelain"], check=False)
    if result.stdout.strip():
        print("⚠️ Warning: Working directory is not clean")
        print(result.stdout)
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # 检查必要的工具
    for tool in ["twine", "build"]:
        result = run_command(["python", "-m", tool, "--version"], check=False)
        if result.returncode != 0:
            print(f"❌ {tool} is not installed. Installing...")
            run_command(["python", "-m", "pip", "install", tool])
    
    print("✅ Prerequisites check completed")

def setup_pypi_config():
    """设置 PyPI 配置"""
    print("\n📝 Setting up PyPI configuration...")
    
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    print("To publish to PyPI, you need an API token.")
    print("1. Go to https://pypi.org/account/register/ to create an account")
    print("2. Go to https://pypi.org/manage/account/#api-tokens to create an API token")
    print("3. Set scope to 'Entire account' for first-time publishing")
    print("4. Copy the token (starts with 'pypi-')")
    
    if pypirc_path.exists():
        print(f"📄 Found existing .pypirc at {pypirc_path}")
        response = input("Use existing configuration? (Y/n): ")
        if response.lower() == 'n':
            setup_new_config(pypirc_path)
    else:
        setup_new_config(pypirc_path)

def setup_new_config(pypirc_path: Path):
    """设置新的 PyPI 配置"""
    print("\n🔐 Setting up new PyPI configuration...")
    
    token = getpass.getpass("Enter your PyPI API token (will be hidden): ")
    if not token.startswith("pypi-"):
        print("⚠️ Warning: Token should start with 'pypi-'")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    config_content = f"""[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = {token}
"""
    
    pypirc_path.write_text(config_content)
    pypirc_path.chmod(0o600)  # 设置为只有用户可读写
    print(f"✅ Configuration saved to {pypirc_path}")

def build_package():
    """构建包"""
    print("\n🏗️ Building package...")
    
    # 清理旧的构建产物
    for pattern in ["build", "dist", "*.egg-info"]:
        run_command(["rm", "-rf"] + [str(p) for p in Path(".").glob(pattern)])
    
    # 构建包
    run_command(["python", "-m", "build"])
    
    # 检查构建的包
    run_command(["python", "-m", "twine", "check", "dist/*"])
    
    print("✅ Package built successfully")

def publish_to_pypi():
    """发布到 PyPI"""
    print("\n🚀 Publishing to PyPI...")
    
    # 列出将要上传的文件
    dist_files = list(Path("dist").glob("*"))
    print("📦 Files to upload:")
    for file in dist_files:
        print(f"   - {file}")
    
    response = input("\nProceed with upload? (y/N): ")
    if response.lower() != 'y':
        print("❌ Upload cancelled")
        return False
    
    # 上传到 PyPI
    try:
        run_command(["python", "-m", "twine", "upload", "dist/*"])
        print("🎉 Successfully published to PyPI!")
        print("📦 Your package is now available at: https://pypi.org/project/zeus-ai/")
        return True
    except SystemExit:
        print("❌ Upload failed. Please check your credentials and try again.")
        return False

def main():
    """主函数"""
    print("🚀 Zeus AI Platform PyPI Publisher")
    print("=" * 50)
    
    # 检查前提条件
    check_prerequisites()
    
    # 设置 PyPI 配置
    setup_pypi_config()
    
    # 构建包
    build_package()
    
    # 发布到 PyPI
    if publish_to_pypi():
        print("\n🎊 Publication completed successfully!")
        print("\nNext steps:")
        print("1. Test installation: pip install zeus-ai-platform")
        print("2. Create GitHub release")
        print("3. Update documentation")
    else:
        print("\n❌ Publication failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
