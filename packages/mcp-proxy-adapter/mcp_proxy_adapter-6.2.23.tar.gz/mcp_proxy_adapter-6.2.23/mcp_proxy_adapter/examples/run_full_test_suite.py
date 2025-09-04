#!/usr/bin/env python3
"""
Full Test Suite Runner for MCP Proxy Adapter
This script automatically runs the complete test suite:
1. Setup test environment
2. Generate configurations
3. Create certificates
4. Run security tests

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status."""
    try:
        print(f"\n🚀 {description}")
        print("=" * 60)

        # Change to script directory if running from package
        script_dir = Path(__file__).parent
        if script_dir.name == "examples":
            os.chdir(script_dir)

        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            check=True,
            cwd=script_dir
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {' '.join(cmd)}")
        print(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False


def main():
    """Run the complete test suite."""
    print("🧪 MCP Proxy Adapter - Full Test Suite")
    print("=" * 60)

    # Check if we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / "setup_test_environment.py").exists():
        print("❌ Please run this script from the examples directory")
        return 1

    success = True

    # 1. Setup test environment
    if not run_command([
        sys.executable, "-m", "mcp_proxy_adapter.examples.setup_test_environment",
        "--output-dir", "."
    ], "Setting up test environment"):
        success = False

    # 2. Generate configurations
    if success and not run_command([
        sys.executable, "-m", "mcp_proxy_adapter.examples.generate_test_configs",
        "--output-dir", "configs"
    ], "Generating test configurations"):
        success = False

    # 3. Create certificates
    if success and not run_command([
        sys.executable, "-m", "mcp_proxy_adapter.examples.create_certificates_simple"
    ], "Creating certificates"):
        success = False

    # 4. Copy roles.json to root directory
    if success:
        import shutil
        from pathlib import Path
        roles_file = Path("configs/roles.json")
        if roles_file.exists():
            shutil.copy2(roles_file, "roles.json")
            print("✅ Copied roles.json to root directory")
        else:
            success = False
            print("❌ roles.json not found in configs directory")

    # 5. Run security tests
    if success and not run_command([
        sys.executable, "-m", "mcp_proxy_adapter.examples.run_security_tests"
    ], "Running security tests"):
        success = False

    # Final result
    print("\n" + "=" * 60)
    if success:
        print("🎉 FULL TEST SUITE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📋 SUMMARY:")
        print("✅ Test environment setup")
        print("✅ Configuration generation")
        print("✅ Certificate creation")
        print("✅ Roles configuration")
        print("✅ Security testing")
        print("\n🚀 All systems are working correctly!")
        return 0
    else:
        print("❌ FULL TEST SUITE FAILED!")
        print("=" * 60)
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check the error messages above")
        print("2. Ensure you have write permissions")
        print("3. Make sure ports 20000-20010 are free")
        print("4. Check if mcp_security_framework is installed")
        return 1


if __name__ == "__main__":
    exit(main())
