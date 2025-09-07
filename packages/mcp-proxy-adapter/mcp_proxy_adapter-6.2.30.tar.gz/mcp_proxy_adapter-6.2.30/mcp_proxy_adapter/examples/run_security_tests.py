#!/usr/bin/env python3
"""
Security Test Runner for MCP Proxy Adapter
This script runs comprehensive security tests against all server configurations:
- Basic HTTP
- HTTP + Token authentication
- HTTPS
- HTTPS + Token authentication
- mTLS
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import asyncio
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

import psutil
import requests
# Import security test client with proper module path
from mcp_proxy_adapter.examples.security_test_client import SecurityTestClient, TestResult
class SecurityTestRunner:
    """Main test runner for security testing."""
    def __init__(self):
        """Initialize test runner."""
        self.servers = {}
        self.proxy_server = None
        self.server_logs = {}
        self.proxy_log = None
        self.test_results = {}
        # Base and proxy ports
        self.base_port = 20000
        self.proxy_port = 20010
        # Server configurations with ports starting from 20000
        self.configs = {
            "basic_http": {
                "config": "configs/http_simple.json",
                "port": self.base_port + 0,
                "url": f"http://localhost:{self.base_port + 0}",
                "auth": "none"
            },
            "http_token": {
                "config": "configs/http_token.json",
                "port": self.base_port + 1,
                "url": f"http://localhost:{self.base_port + 1}",
                "auth": "api_key"
            },
            "https": {
                "config": "configs/https_simple.json",
                "port": self.base_port + 2,
                "url": f"https://localhost:{self.base_port + 2}",
                "auth": "none"
            },
            "https_token": {
                "config": "configs/https_token.json",
                "port": self.base_port + 3,
                "url": f"https://localhost:{self.base_port + 3}",
                "auth": "api_key"
            },
            "mtls": {
                "config": "configs/mtls_no_roles.json",
                "port": self.base_port + 4,
                "url": f"https://localhost:{self.base_port + 4}",
                "auth": "certificate"
            }
        }

    def _port_in_use(self, port: int, host: str = "127.0.0.1") -> bool:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except Exception:
            return False

    def _pids_on_port(self, port: int) -> List[int]:
        pids: List[int] = []
        try:
            for proc in psutil.process_iter(attrs=["pid"]):
                try:
                    connections = proc.connections(kind="inet")
                    for c in connections:
                        if c.laddr and c.laddr.port == port:
                            pids.append(proc.pid)
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        return list(set(pids))

    def ensure_ports_free(self, ports: List[int]) -> None:
        for port in ports:
            pids = self._pids_on_port(port)
            for pid in pids:
                try:
                    psutil.Process(pid).terminate()
                except Exception:
                    pass
            time.sleep(0.3)
            for pid in pids:
                try:
                    if psutil.pid_exists(pid):
                        psutil.Process(pid).kill()
                except Exception:
                    pass

    def wait_for_http(self, url: str, timeout_sec: float = 8.0) -> bool:
        end = time.time() + timeout_sec
        candidates = ["/health", "/proxy/health"]
        while time.time() < end:
            for path in candidates:
                health_url = url.rstrip("/") + path
                try:
                    resp = requests.get(health_url, timeout=1.0, verify=False)
                    if resp.status_code == 200:
                        return True
                except Exception:
                    pass
            time.sleep(0.2)
        return False

    def wait_for_port(self, port: int, timeout_sec: float = 8.0) -> bool:
        end = time.time() + timeout_sec
        while time.time() < end:
            if self._port_in_use(port):
                return True
            time.sleep(0.2)
        return False

    def get_all_ports(self) -> List[int]:
        ports = [self.proxy_port]
        for cfg in self.configs.values():
            ports.append(cfg["port"])
        return list(sorted(set(ports)))

    def _validate_file(self, base: Path, path_value: Optional[str]) -> Tuple[bool, str]:
        if not path_value:
            return True, ""
        p = Path(path_value)
        if not p.is_absolute():
            p = base / p
        return p.exists(), str(p)

    def validate_config_files(self) -> bool:
        ok = True
        base = Path.cwd()
        missing: List[str] = []
        for name, cfg in self.configs.items():
            cfg_path = Path(cfg["config"]).resolve()
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ssl = data.get("ssl", {})
                for key in ("cert_file", "key_file", "ca_cert"):
                    exists, abs_path = self._validate_file(base, ssl.get(key))
                    if ssl.get("enabled") and key in ("cert_file", "key_file") and not exists:
                        ok = False
                        missing.append(f"{name}:{key} -> {abs_path}")
                sec = data.get("security", {})
                perms = sec.get("permissions", {})
                exists, abs_path = self._validate_file(base, perms.get("roles_file"))
                if sec.get("enabled") and perms.get("enabled") and not exists:
                    ok = False
                    missing.append(f"{name}:roles_file -> {abs_path}")
            except Exception as e:
                ok = False
                missing.append(f"{name}: cannot read {cfg_path} ({e})")
        if not ok:
            print("❌ CONFIG VALIDATION FAILED. Missing files:")
            for m in missing:
                print("   -", m)
        else:
            print("✅ Configuration file paths validated")
        return ok
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")
        # Check if we're in the right directory
        if not Path("configs").exists():
            print("❌ configs directory not found. Please run from the test environment root directory.")
            return False
        # Check if certificates exist
        cert_files = [
             "certs/mcp_proxy_adapter_ca_ca.crt",
            "certs/localhost_server.crt",
            "keys/localhost_server.key"
        ]
        
        missing_certs = []
        # Check if roles.json exists
        roles_file = "configs/roles.json"
        if not os.path.exists(roles_file):
            missing_certs.append(f"Missing roles file: {roles_file}")
        for cert_file in cert_files:
            if not Path(cert_file).exists():
                missing_certs.append(cert_file)
        if missing_certs:
            print(f"❌ Missing certificates: {missing_certs}")
            print("💡 Run: python -m mcp_proxy_adapter.examples.setup_test_environment to generate certificates")
            return False
        print("✅ Prerequisites check passed")
        return True
    def start_server(self, name: str, config_path: str, port: int) -> Optional[subprocess.Popen]:
        """Start a server in background."""
        try:
            print(f"🚀 Starting {name} server on port {port}...")
            # Ensure the port is free just before starting
            self.ensure_ports_free([port])
            if self._port_in_use(port):
                print(f"⚠️ Port {port} still busy, waiting...")
                if not self.wait_for_port(port, timeout_sec=1.5):
                    # After wait_for_port True means busy; we invert logic here
                    pass
            # If still busy after attempts, abort this server start
            if self._port_in_use(port):
                print(f"❌ Port {port} is in use, cannot start {name}")
                return None
            # Start server in background
            logs_dir = Path("logs"); logs_dir.mkdir(exist_ok=True)
            log_path = logs_dir / f"{name}.log"
            log_file = open(log_path, "wb")
            self.server_logs[name] = log_file
            process = subprocess.Popen([
                sys.executable, "-m", "mcp_proxy_adapter.main",
                "--config", config_path
            ], stdout=log_file, stderr=subprocess.STDOUT)
            # Wait a bit for server to start
            time.sleep(3)
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {name} server started (PID: {process.pid})")
                return process
            else:
                print(f"❌ Failed to start {name} server (see logs/{name}.log)")
                return None
        except Exception as e:
            print(f"❌ Error starting {name} server: {e}")
            return None
    def stop_server(self, name: str, process: subprocess.Popen):
        """Stop a server."""
        try:
            print(f"🛑 Stopping {name} server (PID: {process.pid})...")
            process.terminate()
            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                print(f"✅ {name} server stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️ Force killing {name} server")
                process.kill()
                process.wait()
        except Exception as e:
            print(f"❌ Error stopping {name} server: {e}")
        finally:
            try:
                lf = self.server_logs.pop(name, None)
                if lf:
                    lf.close()
            except Exception:
                pass

    def start_proxy_server(self) -> bool:
        """Start the proxy server for server registration."""
        try:
            print("🚀 Starting proxy server...")
            # Find the proxy server script
            proxy_script = Path(__file__).parent / "run_proxy_server.py"
            if not proxy_script.exists():
                print("❌ Proxy server script not found")
                return False

            # Start proxy server
            cmd = [sys.executable, str(proxy_script), "--host", "127.0.0.1", "--port", str(self.proxy_port)]
            logs_dir = Path("logs"); logs_dir.mkdir(exist_ok=True)
            proxy_log_path = logs_dir / "proxy_server.log"
            self.proxy_log = open(proxy_log_path, "wb")
            process = subprocess.Popen(
                cmd,
                stdout=self.proxy_log,
                stderr=subprocess.STDOUT,
                cwd=Path.cwd()
            )

            # Check readiness
            if process.poll() is None and self.wait_for_http(f"http://127.0.0.1:{self.proxy_port}"):
                self.proxy_server = process
                print("✅ Proxy server started successfully (PID: {})".format(process.pid))
                return True
            else:
                print("❌ Failed to start proxy server (see logs/proxy_server.log)")
                return False

        except Exception as e:
            print(f"❌ Error starting proxy server: {e}")
            return False

    def stop_proxy_server(self):
        """Stop the proxy server."""
        if self.proxy_server:
            try:
                print("🛑 Stopping proxy server (PID: {})...".format(self.proxy_server.pid))
                self.proxy_server.terminate()
                try:
                    self.proxy_server.wait(timeout=5)
                    print("✅ Proxy server stopped")
                except subprocess.TimeoutExpired:
                    print("⚠️ Force killing proxy server")
                    self.proxy_server.kill()
                    self.proxy_server.wait()
            except Exception as e:
                print(f"❌ Error stopping proxy server: {e}")
            finally:
                self.proxy_server = None
                try:
                    if self.proxy_log:
                        self.proxy_log.close()
                        self.proxy_log = None
                except Exception:
                    pass
    async def test_server(self, name: str, config: Dict[str, Any]) -> List[TestResult]:
        """Test a specific server configuration."""
        print(f"\n🧪 Testing {name} server...")
        print("=" * 50)
        # Create client with appropriate SSL context
        if config["auth"] == "certificate":
            # For mTLS, create client with certificate-based SSL context
            client = SecurityTestClient(config["url"])
            # Override SSL context for mTLS
            client.create_ssl_context = client.create_ssl_context_for_mtls
            async with client as client_session:
                results = await client_session.run_security_tests(
                    config["url"],
                    config["auth"]
                )
        else:
            # For other auth types, use default SSL context
            async with SecurityTestClient(config["url"]) as client:
                results = await client.run_security_tests(
                    config["url"],
                    config["auth"]
                )
        # Print summary for this server
        passed = sum(1 for r in results if r.success)
        total = len(results)
        print(f"\n📊 {name} Results: {passed}/{total} tests passed")
        return results
    async def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run tests against all server configurations."""
        print("🚀 Starting comprehensive security testing")
        print("=" * 60)
        # Start all servers with verification and abort on failure
        for name, config in self.configs.items():
            process = self.start_server(name, config["config"], config["port"])
            if not process:
                print(f"❌ {name} failed to start. Aborting.")
                return {}
            url = config["url"]
            ready = False
            if name == "mtls":
                ready = self.wait_for_port(config["port"], timeout_sec=8.0)
            else:
                ready = self.wait_for_http(url, timeout_sec=8.0)
            if not ready:
                print(f"❌ {name} did not become ready. Aborting.")
                return {}
            self.servers[name] = process
        print("\n✅ All servers started and verified. Proceeding to client tests...")
        # Test each server
        all_results = {}
        for name, config in self.configs.items():
            if name in self.servers:
                try:
                    results = await self.test_server(name, config)
                    all_results[name] = results
                except Exception as e:
                    print(f"❌ Error testing {name}: {e}")
                    all_results[name] = []
            else:
                print(f"⚠️ Skipping {name} tests (server not running)")
                all_results[name] = []
        return all_results
    def print_final_summary(self, all_results: Dict[str, List[TestResult]]):
        """Print final test summary."""
        print("\n" + "=" * 80)
        print("📊 FINAL SECURITY TEST SUMMARY")
        print("=" * 80)
        total_tests = 0
        total_passed = 0
        for server_name, results in all_results.items():
            if results:
                passed = sum(1 for r in results if r.success)
                total = len(results)
                total_tests += total
                total_passed += passed
                status = "✅ PASS" if passed == total else "❌ FAIL"
                print(f"{status} {server_name.upper()}: {passed}/{total} tests passed")
                # Show failed tests
                failed_tests = [r for r in results if not r.success]
                for test in failed_tests:
                    print(f"   ❌ {test.test_name}: {test.error_message}")
            else:
                print(f"⚠️ SKIP {server_name.upper()}: No tests run")
        print("\n" + "-" * 80)
        print(f"OVERALL: {total_passed}/{total_tests} tests passed")
        if total_tests > 0:
            success_rate = (total_passed / total_tests) * 100
            print(f"SUCCESS RATE: {success_rate:.1f}%")
        # Overall status
        if total_passed == total_tests and total_tests > 0:
            print("🎉 ALL TESTS PASSED!")
            print("\n" + "=" * 60)
            print("✅ SECURITY TESTS COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print("\n📋 NEXT STEPS:")
            print("1. Start basic framework example:")
            print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/https_simple.json")
            print("\n2. Start full application example:")
            print("   python -m mcp_proxy_adapter.examples.full_application.main --config configs/mtls_with_roles.json")
            print("\n3. Test with custom configurations:")
            print("   python -m mcp_proxy_adapter.examples.basic_framework.main --config configs/http_simple.json")
            print("=" * 60)
        elif total_passed > 0:
            print("⚠️ SOME TESTS FAILED")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Check if proxy server is running:")
            print("   python /path/to/run_proxy_server.py --host 127.0.0.1 --port 3004")
            print("\n2. Check if certificates are generated:")
            print("   python -m mcp_proxy_adapter.examples.generate_certificates")
            print("\n3. Verify configuration files exist:")
            print("   python -m mcp_proxy_adapter.examples.generate_test_configs --output-dir configs")
            print("\n4. Check if ports are available (3004, 8000-8005)")
            print("=" * 60)
        else:
            print("❌ ALL TESTS FAILED")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Run setup test environment:")
            print("   python -m mcp_proxy_adapter.examples.setup_test_environment")
            print("\n2. Generate certificates:")
            print("   python -m mcp_proxy_adapter.examples.generate_certificates")
            print("\n3. Generate configurations:")
            print("   python -m mcp_proxy_adapter.examples.generate_test_configs --output-dir configs")
            print("\n4. Start proxy server manually if needed:")
            print("   python /path/to/run_proxy_server.py --host 127.0.0.1 --port 3004")
            print("=" * 60)
    def cleanup(self):
        """Cleanup all running servers and proxy."""
        print("\n🧹 Cleaning up...")
        # Stop test servers
        for name, process in self.servers.items():
            self.stop_server(name, process)
        self.servers.clear()
        # Stop proxy server
        self.stop_proxy_server()
    def signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print(f"\n⚠️ Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(0)
    async def run(self):
        """Main run method."""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        try:
            # Check prerequisites
            if not self.check_prerequisites():
                return False

            # Free ports before run
            print("\n🧹 Freeing ports before startup...")
            self.ensure_ports_free(self.get_all_ports())

            # Validate config file paths
            if not self.validate_config_files():
                return False

            # Start proxy server first
            print("\n🚀 Starting proxy server for server registration...")
            if not self.start_proxy_server():
                print("❌ Cannot proceed without proxy server")
                return False

            # Wait for proxy server to be fully ready
            print("⏳ Waiting for proxy server to be ready...")
            time.sleep(3)

            # Run all tests
            all_results = await self.run_all_tests()
            # Print summary
            self.print_final_summary(all_results)
            return True
        except Exception as e:
            print(f"❌ Test runner error: {e}")
            return False
        finally:
            # Always cleanup
            self.cleanup()
def main():
    """Main function."""
    import argparse
    parser = argparse.ArgumentParser(description="Security Test Runner for MCP Proxy Adapter")
    parser.add_argument("--config", help="Test specific configuration")
    parser.add_argument("--no-cleanup", action="store_true", help="Don't cleanup servers after tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Determine the correct configs directory
    current_dir = Path.cwd()
    if (current_dir / "configs").exists():
        # We're in the test environment root directory
        configs_dir = current_dir / "configs"
        os.chdir(current_dir)  # Stay in current directory
    elif (Path(__file__).parent.parent / "configs").exists():
        # We're running from package installation, configs is relative to examples
        configs_dir = Path(__file__).parent.parent / "configs"
        os.chdir(Path(__file__).parent.parent)  # Change to parent of examples
    else:
        # Try to find configs relative to examples directory
        examples_dir = Path(__file__).parent
        configs_dir = examples_dir / "configs"
        os.chdir(examples_dir)

    print(f"🔍 Using configs directory: {configs_dir}")
    print(f"🔍 Working directory: {Path.cwd()}")

    # Create and run test runner
    runner = SecurityTestRunner()
    try:
        success = asyncio.run(runner.run())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()
