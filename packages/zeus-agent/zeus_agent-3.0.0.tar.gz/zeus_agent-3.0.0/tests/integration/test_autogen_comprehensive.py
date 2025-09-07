#!/usr/bin/env python3
"""
AutoGen Adapter Comprehensive Test Runner
Runs complete test suite for AutoGen adapter with proper API key validation
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_environment():
    """Check test environment and API key availability"""
    print("🔍 Checking test environment...")
    
    # Check if AutoGen v0.4 is available
    try:
        import autogen_agentchat
        print("✅ AutoGen v0.4 (autogen-agentchat) is available")
        autogen_available = True
    except ImportError:
        print("❌ AutoGen v0.4 (autogen-agentchat) is not available")
        print("   Install with: pip install autogen-agentchat")
        autogen_available = False
    
    # Check API key availability
    test_api_key = os.getenv("OPENAI_API_KEY_TEST")
    real_api_key = os.getenv("OPENAI_API_KEY")
    
    print(f"🔑 Test API key: {'✅ Available' if test_api_key else '❌ Not set'}")
    print(f"🔑 Real API key: {'✅ Available' if real_api_key else '❌ Not set'}")
    
    if not real_api_key:
        print("\n⚠️  Warning: No real OPENAI_API_KEY found")
        print("   Integration tests will be skipped")
        print("   Set OPENAI_API_KEY to run full integration tests")
    
    return {
        'autogen_available': autogen_available,
        'test_api_key': bool(test_api_key),
        'real_api_key': bool(real_api_key)
    }

def run_unit_tests():
    """Run unit tests (mock-based, no API key required)"""
    print("\n🧪 Running unit tests...")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/unit/adapter/test_autogen_v04_adapter.py",
        "-v",
        "--tb=short",
        "-m", "not integration",  # Skip integration tests
        "--durations=10"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Unit Test Output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0

def run_integration_tests():
    """Run integration tests (require real API key)"""
    print("\n🌐 Running integration tests...")
    
    real_api_key = os.getenv("OPENAI_API_KEY")
    if not real_api_key:
        print("❌ Skipping integration tests - no OPENAI_API_KEY")
        return True
    
    cmd = [
        "python", "-m", "pytest", 
        "tests/unit/adapter/test_autogen_v04_adapter.py",
        "-v",
        "--tb=short",
        "-m", "integration",  # Only integration tests
        "--durations=10",
        "-x"  # Stop on first failure for integration tests
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Integration Test Output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0

def run_all_tests():
    """Run all tests"""
    print("\n🚀 Running all AutoGen adapter tests...")
    
    cmd = [
        "python", "-m", "pytest",
        "tests/unit/adapter/test_autogen_v04_adapter.py",
        "-v",
        "--tb=short",
        "--durations=10",
        "--maxfail=5"  # Stop after 5 failures
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("All Tests Output:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0

def run_coverage_analysis():
    """Run tests with coverage analysis"""
    print("\n📊 Running tests with coverage analysis...")
    
    try:
        import coverage
    except ImportError:
        print("❌ Coverage not available. Install with: pip install coverage")
        return False
    
    cmd = [
        "python", "-m", "coverage", "run",
        "-m", "pytest",
        "tests/unit/adapter/test_autogen_v04_adapter.py",
        "-v"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        # Generate coverage report
        print("\n📈 Coverage Report:")
        subprocess.run(["python", "-m", "coverage", "report", 
                       "--include=layers/adapter/autogen/*"])
        
        # Generate HTML report
        subprocess.run(["python", "-m", "coverage", "html",
                       "--include=layers/adapter/autogen/*",
                       "--directory=htmlcov_autogen"])
        print("📄 HTML coverage report generated in htmlcov_autogen/")
    
    return result.returncode == 0

def validate_api_key_formats():
    """Validate API key formats"""
    print("\n🔍 Validating API key formats...")
    
    test_api_key = os.getenv("OPENAI_API_KEY_TEST", "test-key-12345")
    real_api_key = os.getenv("OPENAI_API_KEY")
    
    # Test API key validation
    valid_formats = [
        "sk-1234567890abcdef",
        "sk-proj-1234567890abcdef",
        test_api_key
    ]
    
    invalid_formats = [
        "",
        "invalid-key", 
        "sk-",
        None
    ]
    
    print("✅ Valid API key formats:")
    for fmt in valid_formats:
        if fmt:
            print(f"   • {fmt[:10]}...")
    
    print("❌ Invalid API key formats:")
    for fmt in invalid_formats:
        print(f"   • {fmt}")
    
    if real_api_key:
        if real_api_key.startswith("sk-"):
            print(f"✅ Real API key format looks valid: {real_api_key[:10]}...")
        else:
            print(f"⚠️  Real API key format may be invalid: {real_api_key[:10]}...")

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="AutoGen Adapter Comprehensive Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--validate-keys", action="store_true", help="Validate API key formats")
    parser.add_argument("--check-env", action="store_true", help="Check environment only")
    
    args = parser.parse_args()
    
    print("🤖 AutoGen Adapter Comprehensive Test Suite")
    print("=" * 50)
    
    # Check environment
    env_status = check_environment()
    
    if args.check_env:
        return 0 if env_status['autogen_available'] else 1
    
    if not env_status['autogen_available']:
        print("❌ Cannot run tests - AutoGen not available")
        return 1
    
    if args.validate_keys:
        validate_api_key_formats()
        return 0
    
    success = True
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.coverage:
        success = run_coverage_analysis()
    else:
        # Run all tests by default
        success = run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 