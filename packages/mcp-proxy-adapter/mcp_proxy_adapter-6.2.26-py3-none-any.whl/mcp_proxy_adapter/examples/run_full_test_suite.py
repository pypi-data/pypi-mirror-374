#!/usr/bin/env python3
"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
Full test suite runner for MCP Proxy Adapter.
Automates the complete testing workflow.
"""
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Optional

class FullTestSuiteRunner:
    """Comprehensive test suite runner that automates the entire testing process."""
    
    def __init__(self):
        """Initialize the test suite runner."""
        self.working_dir = Path.cwd()
        self.configs_dir = self.working_dir / "configs"
        self.certs_dir = self.working_dir / "certs"
        self.keys_dir = self.working_dir / "keys"
        self.roles_file = self.working_dir / "configs" / "roles.json"
        
    def print_step(self, step: str, description: str):
        """Print a formatted step header."""
        print(f"\n{'='*60}")
        print(f"🔧 STEP {step}: {description}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        """Print a success message."""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print an error message."""
        print(f"❌ {message}")
    
    def print_info(self, message: str):
        """Print an info message."""
        print(f"ℹ️  {message}")
    
    def check_environment(self) -> bool:
        """Check if the environment is properly set up."""
        self.print_step("1", "Environment Validation")
        
        # Check if we're in a virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.print_error("Not running in a virtual environment!")
            self.print_info("Please activate your virtual environment first:")
            self.print_info("  source venv/bin/activate  # or .venv/bin/activate")
            return False
        
        self.print_success("Virtual environment is active")
        
        # Check if mcp_proxy_adapter is installed
        try:
            import mcp_proxy_adapter
            self.print_success(f"mcp_proxy_adapter is installed (version: {mcp_proxy_adapter.__version__})")
        except ImportError:
            self.print_error("mcp_proxy_adapter is not installed!")
            self.print_info("Please install it first:")
            self.print_info("  pip install mcp_proxy_adapter")
            return False
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            self.print_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            self.print_error(f"Python {python_version.major}.{python_version.minor} is not supported. Need Python 3.8+")
            return False
        
        return True
    
    def create_directories(self) -> bool:
        """Create necessary directories for testing."""
        self.print_step("2", "Directory Creation")
        
        try:
            # Create configs directory
            self.configs_dir.mkdir(exist_ok=True)
            self.print_success(f"Created/verified configs directory: {self.configs_dir}")
            
            # Create certs directory
            self.certs_dir.mkdir(exist_ok=True)
            self.print_success(f"Created/verified certs directory: {self.certs_dir}")
            
            # Create keys directory
            self.keys_dir.mkdir(exist_ok=True)
            self.print_success(f"Created/verified keys directory: {self.keys_dir}")
            
            return True
            
        except Exception as e:
            self.print_error(f"Failed to create directories: {e}")
            return False
    
    def generate_certificates(self) -> bool:
        """Generate SSL certificates for testing."""
        self.print_step("3", "Certificate Generation")
        
        try:
            # Run certificate generation script
            cmd = [sys.executable, "-m", "mcp_proxy_adapter.examples.create_certificates_simple"]
            self.print_info("Running certificate generation script...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.working_dir)
            
            if result.returncode == 0:
                self.print_success("Certificates generated successfully")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                self.print_error("Certificate generation failed!")
                if result.stderr:
                    print("Error output:")
                    print(result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"Failed to generate certificates: {e}")
            return False
    
    def generate_configurations(self) -> bool:
        """Generate test configurations."""
        self.print_step("4", "Configuration Generation")
        
        try:
            # Run configuration generation script
            cmd = [sys.executable, "-m", "mcp_proxy_adapter.examples.generate_test_configs"]
            self.print_info("Running configuration generation script...")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.working_dir)
            
            if result.returncode == 0:
                self.print_success("Configurations generated successfully")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                self.print_error("Configuration generation failed!")
                if result.stderr:
                    print("Error output:")
                    print(result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"Failed to generate configurations: {e}")
            return False
    
    def run_security_tests(self) -> bool:
        """Run the security test suite."""
        self.print_step("5", "Security Testing")
        
        try:
            # Run security tests
            cmd = [sys.executable, "-m", "mcp_proxy_adapter.examples.run_security_tests", "--verbose"]
            self.print_info("Running security tests...")
            
            # Debug: show current working directory and check files
            self.print_info(f"DEBUG: Current working directory: {os.getcwd()}")
            self.print_info(f"DEBUG: Working directory from class: {self.working_dir}")
            
            # Check if certificates exist before running tests
            localhost_cert = self.certs_dir / "localhost_server.crt"
            self.print_info(f"DEBUG: localhost_server.crt exists: {localhost_cert.exists()}")
            if localhost_cert.exists():
                self.print_info(f"DEBUG: localhost_server.crt is symlink: {localhost_cert.is_symlink()}")
                if localhost_cert.is_symlink():
                    self.print_info(f"DEBUG: localhost_server.crt symlink target: {localhost_cert.readlink()}")
            
            # List all files in certs directory
            self.print_info("DEBUG: Files in certs directory:")
            for file in self.certs_dir.iterdir():
                self.print_info(f"DEBUG:   {file.name} -> {file}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.working_dir)
            
            if result.returncode == 0:
                self.print_success("Security tests completed successfully!")
                if result.stdout:
                    print(result.stdout)
                return True
            else:
                self.print_error("Security tests failed!")
                if result.stdout:
                    print("Test output:")
                    print(result.stdout)
                if result.stderr:
                    print("Error output:")
                    print(result.stderr)
                return False
                
        except Exception as e:
            self.print_error(f"Failed to run security tests: {e}")
            return False
    
    def cleanup(self):
        """Clean up temporary files and processes."""
        self.print_info("Cleaning up...")
        
        # Simple cleanup - just print success message
        # Process cleanup is handled by the test scripts themselves
        print("✅ Cleanup completed")
    


    def cleanup_directories(self) -> bool:
        """Clean up existing test directories before starting."""
        self.print_info("Cleaning up existing test directories...")
        
        try:
            import shutil
            
            # Directories to clean
            dirs_to_clean = [self.configs_dir, self.certs_dir, self.keys_dir]
            files_to_clean = [self.working_dir / "roles.json"]
            
            # Remove directories
            for dir_path in dirs_to_clean:
                if dir_path.exists():
                    shutil.rmtree(dir_path)
                    print(f"🗑️  Removed directory: {dir_path}")
            
            # Remove files
            for file_path in files_to_clean:
                if file_path.exists():
                    file_path.unlink()
                    print(f"🗑️  Removed file: {file_path}")
            
            self.print_success("Directory cleanup completed")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to cleanup directories: {e}")
            return False
    
    def run_full_suite(self) -> bool:
        """Run the complete test suite."""
        print("🚀 MCP Proxy Adapter - Full Test Suite")
        print("=" * 60)
        print(f"Working directory: {self.working_dir}")
        print(f"Python executable: {sys.executable}")
        
        try:
            # Step 0: Clean up existing directories
            if not self.cleanup_directories():
                return False
            
            # Step 1: Environment validation
            if not self.check_environment():
                return False
            
            # Step 2: Directory creation
            if not self.create_directories():
                return False
            
            # Step 3: Certificate generation
            if not self.generate_certificates():
                return False
            
            # Step 4: Configuration generation
            if not self.generate_configurations():
                return False
            
            # Step 5: Security testing
            if not self.run_security_tests():
                return False
            
            # All steps completed successfully
            print(f"\n{'='*60}")
            print("🎉 FULL TEST SUITE COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("✅ Environment validated")
            print("✅ Directories cleaned")
            print("✅ Directories created")
            print("✅ Certificates generated")
            print("✅ Configurations generated")
            print("✅ Security tests passed")
            print(f"\n📁 Test artifacts created in: {self.working_dir}")
            print(f"📁 Configurations: {self.configs_dir}")
            print(f"📁 Certificates: {self.certs_dir}")
            print(f"📁 Keys: {self.keys_dir}")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Test suite interrupted by user")
            return False
        except Exception as e:
            self.print_error(f"Unexpected error during test suite execution: {e}")
            return False
        finally:
            try:
                self.print_info("Starting cleanup in finally block...")
                self.cleanup()
                self.print_info("Cleanup in finally block completed")
            except Exception as e:
                self.print_error(f"Cleanup failed in finally block: {e}")
                import traceback
                traceback.print_exc()

def main():
    """Main entry point."""
    runner = FullTestSuiteRunner()
    
    try:
        success = runner.run_full_suite()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
