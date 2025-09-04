"""
OAuth Callback Server for Automated Authorization Code Capture

This module provides a lightweight HTTPS server that listens on localhost:8080
to automatically capture OAuth authorization codes from Yahoo's redirect.
"""

import os
import ssl
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any, Union, Protocol
import tempfile
import time
import logging

logger = logging.getLogger(__name__)


class OAuthHTTPServer(Protocol):
    """Protocol for HTTPServer with OAuth attributes."""
    oauth_code: Optional[str]
    oauth_error: Optional[str]
    oauth_received: bool
    timeout: int
    
    def handle_request(self) -> None: ...
    def server_close(self) -> None: ...


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback capture."""

    def do_GET(self):
        """Handle GET request from Yahoo OAuth redirect."""
        try:
            # Parse the URL and extract parameters
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)

            # Check for authorization code
            if 'code' in query_params:
                code = query_params['code'][0]

                # Store the code in the server instance
                self.server.oauth_code = code  # type: ignore
                self.server.oauth_received = True  # type: ignore

                # Send success response to browser
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                success_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>OAuth Success</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .success {{ color: #28a745; font-size: 24px; }}
                        .code {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <div class="success">SUCCESS: OAuth Authorization Successful!</div>
                    <p>Authorization code received successfully.</p>
                    <div class="code">Code: {code}</div>
                    <p>You can close this window. The MCP server will continue automatically.</p>
                    <script>
                        setTimeout(function() {{
                            window.close();
                        }}, 3000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(success_html.encode())

                logger.info(f"OAuth code captured: {code[:10]}...")

            elif 'error' in query_params:
                error = query_params['error'][0]
                error_description = query_params.get('error_description', ['Unknown error'])[0]

                self.server.oauth_error = f"{error}: {error_description}"  # type: ignore
                self.server.oauth_received = True  # type: ignore

                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>OAuth Error</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                        .error {{ color: #dc3545; font-size: 24px; }}
                    </style>
                </head>
                <body>
                    <div class="error">ERROR: OAuth Authorization Failed</div>
                    <p>Error: {error}</p>
                    <p>Description: {error_description}</p>
                    <p>Please try again or contact support.</p>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode())

                logger.error(f"OAuth error received: {error} - {error_description}")

            else:
                # No code or error - unexpected request
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                self.wfile.write(b"""
                <!DOCTYPE html>
                <html>
                <body>
                    <h1>OAuth Callback Server</h1>
                    <p>Waiting for OAuth authorization...</p>
                </body>
                </html>
                """)

        except Exception as e:
            logger.error(f"Error handling OAuth callback: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def log_message(self, format, *args):
        """Suppress default HTTP logging."""
        pass


class OAuthCallbackServer:
    """Manages the OAuth callback server lifecycle."""

    def __init__(self, port: int = 8080):
        self.port = port
        self.server: Optional[OAuthHTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        self.cert_file: Optional[str] = None
        self.key_file: Optional[str] = None

    def _create_self_signed_cert(self) -> tuple[str, str]:
        """Create a self-signed SSL certificate for HTTPS."""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import datetime
            import ipaddress

            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])

            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())

            # Write certificate and key to temporary files
            temp_dir = tempfile.mkdtemp()
            cert_file = os.path.join(temp_dir, 'cert.pem')
            key_file = os.path.join(temp_dir, 'key.pem')

            with open(cert_file, 'wb') as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))

            with open(key_file, 'wb') as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            return cert_file, key_file

        except ImportError:
            logger.warning("cryptography package not available, falling back to OpenSSL")
            return self._create_cert_with_openssl()

    def _create_cert_with_openssl(self) -> tuple[str, str]:
        """Fallback: create certificate using OpenSSL command or use HTTP instead."""
        import subprocess

        temp_dir = tempfile.mkdtemp()
        cert_file = os.path.join(temp_dir, 'cert.pem')
        key_file = os.path.join(temp_dir, 'key.pem')

        try:
            # Try OpenSSL first
            cmd = [
                'openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-keyout', key_file,
                '-out', cert_file, '-days', '365', '-nodes', '-subj', '/CN=localhost'
            ]

            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return cert_file, key_file

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.warning(f"OpenSSL certificate creation failed: {e}")
            # For testing purposes, we can fall back to HTTP
            # This is not ideal for production but allows testing
            raise RuntimeError(
                "SSL certificate creation failed. For production use, install 'cryptography' package or OpenSSL. "
                "As a fallback, you can modify your Yahoo app to use 'urn:ietf:wg:oauth:2.0:oob' redirect URI."
            )

    def start_server(self, timeout: int = 300) -> None:
        """Start the HTTPS callback server."""
        try:
            # Create SSL certificate
            cert_file, key_file = self._create_self_signed_cert()
            self.cert_file = cert_file
            self.key_file = key_file

            # Create server
            server = HTTPServer(('localhost', self.port), OAuthCallbackHandler)
            
            # Add SSL context
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(cert_file, key_file)
            server.socket = context.wrap_socket(server.socket, server_side=True)

            # Initialize server attributes (dynamically added)
            server.oauth_code = None  # type: ignore
            server.oauth_error = None  # type: ignore
            server.oauth_received = False  # type: ignore
            server.timeout = 1  # type: ignore  # Short timeout for periodic checks
            
            # Cast to our protocol type for proper typing
            self.server = server  # type: ignore[assignment]

            logger.info(f"Starting OAuth callback server on https://localhost:{self.port}")

            # Start server in background thread
            def run_server() -> None:
                try:
                    if self.server:
                        start_time = time.time()
                        while not self.server.oauth_received and (time.time() - start_time < timeout):
                            self.server.handle_request()

                        if not self.server.oauth_received:
                            logger.warning(f"OAuth callback server timed out after {timeout} seconds")

                except Exception as e:
                    logger.error(f"OAuth callback server error: {e}")

            server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread = server_thread
            server_thread.start()

        except Exception as e:
            self.cleanup()
            raise RuntimeError(f"Failed to start OAuth callback server: {e}")

    def wait_for_code(self, timeout: int = 300) -> Optional[str]:
        """Wait for OAuth authorization code."""
        if not self.server:
            raise RuntimeError("Server not started")

        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.server.oauth_received:
                if self.server.oauth_error:
                    raise RuntimeError(f"OAuth error: {self.server.oauth_error}")
                return self.server.oauth_code

            time.sleep(0.5)

        raise TimeoutError(f"OAuth callback timed out after {timeout} seconds")

    def cleanup(self) -> None:
        """Clean up server resources."""
        if self.server:
            try:
                self.server.server_close()
            except (OSError, AttributeError):
                pass
            self.server = None

        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1)
            self.server_thread = None

        # Clean up certificate files
        for cert_path in [self.cert_file, self.key_file]:
            if cert_path and os.path.exists(cert_path):
                try:
                    os.unlink(cert_path)
                    # Try to remove temp directory
                    temp_dir = os.path.dirname(cert_path)
                    if os.path.exists(temp_dir):
                        os.rmdir(temp_dir)
                except (OSError, FileNotFoundError):
                    pass


def automated_oauth_flow(auth_manager: Any, open_browser: bool = True, timeout: int = 300) -> Dict[str, Any]:
    """
    Perform automated OAuth flow with callback server.

    Args:
        auth_manager: EnhancedYahooAuthManager instance
        open_browser: Whether to automatically open browser
        timeout: Timeout in seconds for OAuth completion

    Returns:
        Dictionary with success status and details
    """
    server: Optional[OAuthCallbackServer] = None

    try:
        # Start callback server
        logger.info("Starting automated OAuth flow...")
        server = OAuthCallbackServer()
        server.start_server(timeout=timeout)

        # Wait a moment for server to start
        time.sleep(1)

        # Get authorization URL
        auth_url = auth_manager.get_authorization_url()
        logger.info(f"Authorization URL: {auth_url}")

        # Open browser if requested
        if open_browser:
            try:
                webbrowser.open(auth_url)
                logger.info("Opened browser for OAuth authorization")
            except Exception as e:
                logger.warning(f"Could not open browser: {e}")

        # Wait for OAuth code
        print("Waiting for OAuth authorization...")
        print(f"If browser didn't open, visit: {auth_url}")
        print("Waiting for you to authorize the application...")

        code = server.wait_for_code(timeout=timeout)

        if code:
            # Exchange code for tokens
            logger.info("Authorization code received, exchanging for tokens...")
            success = auth_manager.exchange_code_for_tokens(code)

            if success:
                return {
                    "status": "success",
                    "message": "Automated OAuth flow completed successfully!",
                    "details": "Authorization code captured automatically and tokens saved.",
                    "authorization_code": code,
                    "token_status": auth_manager.get_token_status()
                }
            else:
                return {
                    "status": "error",
                    "message": "Token exchange failed",
                    "details": "Authorization code was captured but token exchange failed.",
                    "authorization_code": code
                }
        else:
            return {
                "status": "error",
                "message": "No authorization code received",
                "details": f"Callback server timed out after {timeout} seconds"
            }

    except Exception as e:
        logger.error(f"Automated OAuth flow failed: {e}")
        return {
            "status": "error",
            "message": f"Automated OAuth flow failed: {str(e)}",
            "details": "Check server logs for more information"
        }

    finally:
        if server:
            server.cleanup()
