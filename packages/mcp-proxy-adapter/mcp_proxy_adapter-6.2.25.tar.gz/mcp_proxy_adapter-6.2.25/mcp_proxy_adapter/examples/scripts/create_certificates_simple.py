#!/usr/bin/env python3
"""
Simple Certificate Creation Script
This script creates basic certificates for testing using mcp_security_framework.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import os
import subprocess
import sys
import argparse
from pathlib import Path
# Import mcp_security_framework
try:
    from mcp_security_framework.core.cert_manager import CertificateManager
    from mcp_security_framework.schemas.config import CertificateConfig, CAConfig, ServerCertConfig, ClientCertConfig
    from mcp_security_framework.schemas.models import CertificateType
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    SECURITY_FRAMEWORK_AVAILABLE = False
    print("Warning: mcp_security_framework not available, falling back to OpenSSL")
class SimpleCertificateCreator:
    """Create certificates using OpenSSL directly."""
    def __init__(self, certs_dir: str = None, keys_dir: str = None):
        # Use current working directory as base
        cwd = Path.cwd()

        if certs_dir:
            self.certs_dir = Path(certs_dir).resolve()
        else:
            self.certs_dir = cwd / "certs"

        if keys_dir:
            self.keys_dir = Path(keys_dir).resolve()
        else:
            self.keys_dir = cwd / "keys"
        # Create directories
        self.certs_dir.mkdir(parents=True, exist_ok=True)
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        print(f"🔧 Using certificates directory: {self.certs_dir}")
        print(f"🔧 Using keys directory: {self.keys_dir}")
    def run_command(self, cmd: list, description: str) -> bool:
        """Run a command and handle errors."""
        try:
            print(f"🔧 {description}...")
            # Use current working directory instead of project_root
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
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
    def create_ca_certificate(self) -> bool:
        """Create CA certificate using mcp_security_framework or OpenSSL fallback."""
        ca_cert_path = self.certs_dir / "ca_cert.pem"
        ca_key_path = self.keys_dir / "ca_key.pem"
        if ca_cert_path.exists() and ca_key_path.exists():
            print(f"ℹ️ CA certificate already exists: {ca_cert_path}")
            return True
        if SECURITY_FRAMEWORK_AVAILABLE:
            return self._create_ca_certificate_with_framework()
        else:
            return self._create_ca_certificate_with_openssl()
    def _create_ca_certificate_with_framework(self) -> bool:
        """Create CA certificate using mcp_security_framework."""
        try:
            print("🔧 Creating CA certificate using mcp_security_framework...")
            # Create CA certificate configuration
            ca_config = CAConfig(
                common_name="mcp_proxy_adapter_test_ca",
                organization="Test Organization",
                organizational_unit="Test Unit",
                country="US",
                state="Test State",
                locality="Test City",
                validity_years=10
            )
            # Create certificate manager
            cert_config = CertificateConfig(
                cert_storage_path=str(self.certs_dir),
                key_storage_path=str(self.keys_dir),
                default_validity_days=365,
                key_size=2048,
                hash_algorithm="sha256"
            )
            cert_manager = CertificateManager(cert_config)
            # Create CA certificate
            cert_pair = cert_manager.create_root_ca(ca_config)
            if cert_pair and cert_pair.certificate_path and cert_pair.private_key_path:
                # Rename the generated files to the expected names
                generated_cert = Path(cert_pair.certificate_path)
                generated_key = Path(cert_pair.private_key_path)
                if generated_cert.exists() and generated_key.exists():
                    # Move to expected names
                    expected_cert = self.certs_dir / "ca_cert.pem"
                    expected_key = self.keys_dir / "ca_key.pem"
                    generated_cert.rename(expected_cert)
                    generated_key.rename(expected_key)
                    print("✅ CA certificate created successfully using mcp_security_framework")
                    return True
                else:
                    print("❌ Generated CA certificate files not found")
                    return False
            else:
                print("❌ Failed to create CA certificate: Invalid certificate pair")
                return False
        except Exception as e:
            print(f"❌ Error creating CA certificate with framework: {e}")
            return False
    def _create_ca_certificate_with_openssl(self) -> bool:
        """Create CA certificate using OpenSSL fallback."""
        ca_cert_path = self.certs_dir / "ca_cert.pem"
        ca_key_path = self.keys_dir / "ca_key.pem"
        # Create CA private key
        key_cmd = [
            "openssl", "genrsa", "-out", str(ca_key_path), "2048"
        ]
        if not self.run_command(key_cmd, "Creating CA private key"):
            return False
        # Create CA certificate
        cert_cmd = [
            "openssl", "req", "-new", "-x509", "-days", "3650",
            "-key", str(ca_key_path),
            "-out", str(ca_cert_path),
            "-subj", "/C=US/ST=Test State/L=Test City/O=Test Organization/CN=MCP Proxy Adapter Test CA"
        ]
        return self.run_command(cert_cmd, "Creating CA certificate")
    def create_server_certificate(self) -> bool:
        """Create server certificate using mcp_security_framework or OpenSSL fallback."""
        server_cert_path = self.certs_dir / "server_cert.pem"
        server_key_path = self.certs_dir / "server_key.pem"
        if server_cert_path.exists() and server_key_path.exists():
            print("ℹ️ Server certificate already exists")
            return True
        if SECURITY_FRAMEWORK_AVAILABLE:
            return self._create_server_certificate_with_framework()
        else:
            return self._create_server_certificate_with_openssl()
    def _create_server_certificate_with_framework(self) -> bool:
        """Create server certificate using mcp_security_framework."""
        try:
            print("🔧 Creating server certificate using mcp_security_framework...")
            # Find CA certificate and key files
            ca_cert_path = None
            ca_key_path = None
            # Look for CA certificate files with expected names
            expected_ca_cert = self.certs_dir / "ca_cert.pem"
            expected_ca_key = self.keys_dir / "ca_key.pem"
            if expected_ca_cert.exists():
                ca_cert_path = str(expected_ca_cert)
            else:
                # Fallback: look for CA certificate files with pattern
                for cert_file in self.certs_dir.glob("*_ca.crt"):
                    ca_cert_path = str(cert_file)
                    break
            if expected_ca_key.exists():
                ca_key_path = str(expected_ca_key)
            else:
                # Fallback: look for CA key files with pattern
                for key_file in self.keys_dir.glob("*_ca.key"):
                    ca_key_path = str(key_file)
                    break
            if not ca_cert_path or not ca_key_path:
                print("❌ CA certificate or key not found")
                return False
            # Create server certificate configuration
            server_config = ServerCertConfig(
                common_name="localhost",
                organization="Test Organization",
                organizational_unit="Test Unit",
                country="US",
                state="Test State",
                locality="Test City",
                subject_alt_names=["localhost", "127.0.0.1"],
                validity_years=1,
                ca_cert_path=ca_cert_path,
                ca_key_path=ca_key_path
            )
            # Create certificate manager
            cert_config = CertificateConfig(
                cert_storage_path=str(self.certs_dir),
                key_storage_path=str(self.certs_dir),  # Server keys in certs dir
                default_validity_days=365,
                key_size=2048,
                hash_algorithm="sha256"
            )
            cert_manager = CertificateManager(cert_config)
            # Create server certificate
            cert_pair = cert_manager.create_server_certificate(server_config)
            if cert_pair and cert_pair.certificate_path and cert_pair.private_key_path:
                # Rename the generated files to the expected names
                generated_cert = Path(cert_pair.certificate_path)
                generated_key = Path(cert_pair.private_key_path)
                if generated_cert.exists() and generated_key.exists():
                    # Move to expected names
                    generated_cert.rename(self.certs_dir / "server_cert.pem")
                    generated_key.rename(self.certs_dir / "server_key.pem")
                    print("✅ Server certificate created successfully using mcp_security_framework")
                    return True
                else:
                    print("❌ Generated certificate files not found")
                    return False
            else:
                print("❌ Failed to create server certificate: Invalid certificate pair")
                return False
        except Exception as e:
            print(f"❌ Error creating server certificate with framework: {e}")
            return False
    def _create_server_certificate_with_openssl(self) -> bool:
        """Create server certificate using OpenSSL fallback."""
        server_cert_path = self.certs_dir / "server_cert.pem"
        server_key_path = self.certs_dir / "server_key.pem"
        # Create server private key
        key_cmd = [
            "openssl", "genrsa", "-out", str(server_key_path), "2048"
        ]
        if not self.run_command(key_cmd, "Creating server private key"):
            return False
        # Create server certificate signing request
        csr_path = self.certs_dir / "server.csr"
        csr_cmd = [
            "openssl", "req", "-new",
            "-key", str(server_key_path),
            "-out", str(csr_path),
            "-subj", "/C=US/ST=Test State/L=Test City/O=Test Organization/CN=localhost"
        ]
        if not self.run_command(csr_cmd, "Creating server CSR"):
            return False
        # Create server certificate
        cert_cmd = [
            "openssl", "x509", "-req", "-days", "730",
            "-in", str(csr_path),
            "-CA", str(self.certs_dir / "ca_cert.pem"),
            "-CAkey", str(self.keys_dir / "ca_key.pem"),
            "-CAcreateserial",
            "-out", str(server_cert_path)
        ]
        success = self.run_command(cert_cmd, "Creating server certificate")
        # Clean up CSR
        if csr_path.exists():
            csr_path.unlink()
        return success
    def create_client_certificate(self, name: str, common_name: str, roles: list = None, permissions: list = None) -> bool:
        """Create client certificate using mcp_security_framework or OpenSSL fallback."""
        cert_path = self.certs_dir / f"{name}_cert.pem"
        key_path = self.certs_dir / f"{name}_key.pem"
        if cert_path.exists() and key_path.exists():
            print(f"ℹ️ Client certificate {name} already exists: {cert_path}")
            return True
        if SECURITY_FRAMEWORK_AVAILABLE:
            return self._create_client_certificate_with_framework(name, common_name, roles, permissions)
        else:
            return self._create_client_certificate_with_openssl(name, common_name)
    def _create_client_certificate_with_framework(self, name: str, common_name: str, roles: list = None, permissions: list = None) -> bool:
        """Create client certificate using mcp_security_framework."""
        try:
            print(f"🔧 Creating client certificate {name} using mcp_security_framework...")
            # Find CA certificate and key files
            ca_cert_path = None
            ca_key_path = None
            # Look for CA certificate files with expected names
            expected_ca_cert = self.certs_dir / "ca_cert.pem"
            expected_ca_key = self.keys_dir / "ca_key.pem"
            if expected_ca_cert.exists():
                ca_cert_path = str(expected_ca_cert)
            else:
                # Fallback: look for CA certificate files with pattern
                for cert_file in self.certs_dir.glob("*_ca.crt"):
                    ca_cert_path = str(cert_file)
                    break
            if expected_ca_key.exists():
                ca_key_path = str(expected_ca_key)
            else:
                # Fallback: look for CA key files with pattern
                for key_file in self.keys_dir.glob("*_ca.key"):
                    ca_key_path = str(key_file)
                    break
            if not ca_cert_path or not ca_key_path:
                print("❌ CA certificate or key not found")
                return False
            # Create client certificate configuration
            client_config = ClientCertConfig(
                common_name=common_name,
                organization="Test Organization",
                organizational_unit="Test Unit",
                country="US",
                state="Test State",
                locality="Test City",
                validity_years=1,
                ca_cert_path=ca_cert_path,
                ca_key_path=ca_key_path
            )
            # Create certificate manager
            cert_config = CertificateConfig(
                cert_storage_path=str(self.certs_dir),
                key_storage_path=str(self.certs_dir),  # Client keys in certs dir
                default_validity_days=365,
                key_size=2048,
                hash_algorithm="sha256"
            )
            cert_manager = CertificateManager(cert_config)
            # Create client certificate
            cert_pair = cert_manager.create_client_certificate(client_config)
            if cert_pair and cert_pair.certificate_path and cert_pair.private_key_path:
                # Rename the generated files to the expected names
                generated_cert = Path(cert_pair.certificate_path)
                generated_key = Path(cert_pair.private_key_path)
                if generated_cert.exists() and generated_key.exists():
                    # Move to expected names
                    expected_cert = self.certs_dir / f"{name}_cert.pem"
                    expected_key = self.certs_dir / f"{name}_key.pem"
                    generated_cert.rename(expected_cert)
                    generated_key.rename(expected_key)
                    print(f"✅ Client certificate {name} created successfully using mcp_security_framework")
                    return True
                else:
                    print(f"❌ Generated certificate files not found for {name}")
                    return False
            else:
                print(f"❌ Failed to create client certificate {name}: Invalid certificate pair")
                return False
        except Exception as e:
            print(f"❌ Error creating client certificate {name} with framework: {e}")
            return False
    def _create_client_certificate_with_openssl(self, name: str, common_name: str) -> bool:
        """Create client certificate using OpenSSL fallback."""
        cert_path = self.certs_dir / f"{name}_cert.pem"
        key_path = self.certs_dir / f"{name}_key.pem"
        # Create client private key
        key_cmd = [
            "openssl", "genrsa", "-out", str(key_path), "2048"
        ]
        if not self.run_command(key_cmd, f"Creating {name} private key"):
            return False
        # Create client certificate signing request
        csr_path = self.certs_dir / f"{name}.csr"
        csr_cmd = [
            "openssl", "req", "-new",
            "-key", str(key_path),
            "-out", str(csr_path),
            "-subj", f"/C=US/ST=Test State/L=Test City/O=Test Organization/CN={common_name}"
        ]
        if not self.run_command(csr_cmd, f"Creating {name} CSR"):
            return False
        # Create client certificate
        cert_cmd = [
            "openssl", "x509", "-req", "-days", "730",
            "-in", str(csr_path),
            "-CA", str(self.certs_dir / "ca_cert.pem"),
            "-CAkey", str(self.keys_dir / "ca_key.pem"),
            "-CAcreateserial",
            "-out", str(cert_path)
        ]
        success = self.run_command(cert_cmd, f"Creating {name} certificate")
        # Clean up CSR
        if csr_path.exists():
            csr_path.unlink()
        return success
    def create_legacy_certificates(self) -> bool:
        """Create legacy certificate files for compatibility."""
        legacy_files = [
            ("client_admin.crt", "client_admin.key", "admin"),
            ("admin.crt", "admin.key", "admin"),
            ("user.crt", "user.key", "user"),
            ("readonly.crt", "readonly.key", "readonly")
        ]
        success = True
        for cert_file, key_file, source_name in legacy_files:
            cert_path = self.certs_dir / cert_file
            key_path = self.certs_dir / key_file
            if not cert_path.exists() or not key_path.exists():
                source_cert = self.certs_dir / f"{source_name}_cert.pem"
                source_key = self.certs_dir / f"{source_name}_key.pem"
                if source_cert.exists() and source_key.exists():
                    self.run_command(["cp", str(source_cert), str(cert_path)], f"Creating {cert_file}")
                    self.run_command(["cp", str(source_key), str(key_path)], f"Creating {key_file}")
                else:
                    print(f"⚠️ Source certificate {source_name} not found for {cert_file}")
                    # Don't fail the entire process for missing legacy certificates
                    continue
        return True  # Always return True for legacy certificates
    def validate_certificates(self) -> bool:
        """Validate all created certificates."""
        print("\n🔍 Validating certificates...")
        cert_files = [
            "ca_cert.pem",
            "server_cert.pem",
            "admin_cert.pem",
            "user_cert.pem",
            "readonly_cert.pem",
            "guest_cert.pem",
            "proxy_cert.pem"
        ]
        success = True
        for cert_file in cert_files:
            cert_path = self.certs_dir / cert_file
            if cert_path.exists():
                try:
                    result = subprocess.run(
                        ["openssl", "x509", "-in", str(cert_path), "-text", "-noout"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    print(f"✅ {cert_file}: Valid")
                except subprocess.CalledProcessError:
                    print(f"❌ {cert_file}: Invalid")
                    success = False
            else:
                print(f"⚠️ {cert_file}: Not found")
        return success
    def create_all(self) -> bool:
        """Create all certificates."""
        print("🔐 Creating All Certificates for Security Testing")
        print("=" * 60)
        success = True
        # 1. Create CA certificate
        if not self.create_ca_certificate():
            success = False
            print("❌ Cannot continue without CA certificate")
            return False
        # 2. Create server certificate
        if not self.create_server_certificate():
            success = False
        # 3. Create client certificates
        print("\n👥 Creating client certificates...")
        client_certs = [
            ("admin", "admin-client", ["admin"], ["read", "write", "execute", "delete", "admin", "register", "unregister", "heartbeat", "discover"]),
            ("user", "user-client", ["user"], ["read", "execute", "register", "unregister", "heartbeat", "discover"]),
            ("readonly", "readonly-client", ["readonly"], ["read", "discover"]),
            ("guest", "guest-client", ["guest"], ["read", "discover"]),
            ("proxy", "proxy-client", ["proxy"], ["register", "unregister", "heartbeat", "discover"])
        ]
        for name, common_name, roles, permissions in client_certs:
            if not self.create_client_certificate(name, common_name, roles, permissions):
                success = False
        # 4. Create legacy certificates
        print("\n🔄 Creating legacy certificates...")
        if not self.create_legacy_certificates():
            success = False
        # 5. Validate certificates
        if not self.validate_certificates():
            success = False
        # Create compatibility symlinks
        if success:
            # CA certificate symlink
            ca_cert = self.certs_dir / "ca_cert.pem"
            expected_ca_cert = self.certs_dir / "mcp_proxy_adapter_ca_ca.crt"
            if ca_cert.exists() and not expected_ca_cert.exists():
                try:
                    expected_ca_cert.symlink_to(ca_cert)
                    print(f"✅ Created CA certificate symlink: {expected_ca_cert}")
                except OSError:
                    # On Windows, symlink might require admin privileges, copy instead
                    import shutil
                    shutil.copy2(ca_cert, expected_ca_cert)
                    print(f"✅ Created CA certificate copy: {expected_ca_cert}")

            # Server certificate symlink
            server_cert = self.certs_dir / "server_cert.pem"
            expected_server_cert = self.certs_dir / "localhost_server.crt"
            if server_cert.exists() and not expected_server_cert.exists():
                try:
                    expected_server_cert.symlink_to(server_cert)
                    print(f"✅ Created server certificate symlink: {expected_server_cert}")
                except OSError:
                    # On Windows, symlink might require admin privileges, copy instead
                    import shutil
                    shutil.copy2(server_cert, expected_server_cert)
                    print(f"✅ Created server certificate copy: {expected_server_cert}")

            # Server key symlink - check if it's in certs or keys directory
            server_key_certs = self.certs_dir / "server_key.pem"
            server_key_keys = self.keys_dir / "server_key.pem"

            if server_key_certs.exists():
                # Server key is in certs directory, move it to keys directory
                import shutil
                shutil.move(str(server_key_certs), str(server_key_keys))
                print(f"✅ Moved server key to keys directory: {server_key_keys}")

            if server_key_keys.exists():
                expected_server_key = self.keys_dir / "localhost_server.key"
                if not expected_server_key.exists():
                    try:
                        expected_server_key.symlink_to(server_key_keys)
                        print(f"✅ Created server key symlink: {expected_server_key}")
                    except OSError:
                        # On Windows, symlink might require admin privileges, copy instead
                        import shutil
                        shutil.copy2(server_key_keys, expected_server_key)
                        print(f"✅ Created server key copy: {expected_server_key}")

        # Print summary
        print("\n" + "=" * 60)
        print("📊 CERTIFICATE CREATION SUMMARY")
        print("=" * 60)
        if success:
            print("✅ All certificates created successfully!")
            print(f"📁 Certificates directory: {self.certs_dir}")
            print(f"🔑 Keys directory: {self.keys_dir}")
            print("\n📋 Created certificates:")
            cert_files = list(self.certs_dir.glob("*.pem")) + list(self.certs_dir.glob("*.crt"))
            for cert_file in sorted(cert_files):
                print(f"   - {cert_file.name}")
            key_files = list(self.keys_dir.glob("*.pem")) + list(self.keys_dir.glob("*.key"))
            for key_file in sorted(key_files):
                print(f"   - {key_file.name}")
        else:
            print("❌ Some certificates failed to create")
            print("Check the error messages above")
        return success
def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create certificates for testing")
    parser.add_argument("--certs-dir", help="Directory for certificates (default: ./certs)")
    parser.add_argument("--keys-dir", help="Directory for keys (default: ./keys)")
    args = parser.parse_args()

    # If no directories specified, check if we're in a test environment
    if not args.certs_dir and not args.keys_dir:
        cwd = Path.cwd()
        # Check if we're in a test environment by looking for typical directories
        if (cwd / "configs").exists() and (cwd / "examples").exists():
            # We're in a test environment, use current directory
            certs_dir = cwd / "certs"
            keys_dir = cwd / "keys"
        else:
            # Use default project structure
            certs_dir = None
            keys_dir = None
    else:
        certs_dir = args.certs_dir
        keys_dir = args.keys_dir

    creator = SimpleCertificateCreator(
        certs_dir=certs_dir,
        keys_dir=keys_dir
    )
    try:
        success = creator.create_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Certificate creation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Certificate creation failed: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()
