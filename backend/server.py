import socket
import threading
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Change these imports to use relative paths
from .config import SERVER_CONFIG
from .database.connection import create_tables
from .routes.auth import handle_auth_routes
from .routes.devices import handle_device_routes
from .routes.locations import handle_location_routes
from .utils.http import error_response, parse_json_body
from .utils.rate_limit import is_rate_limited

class RequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        self._handle_request('GET')

    def do_POST(self):
        """Handle POST requests."""
        self._handle_request('POST')

    def do_PUT(self):
        """Handle PUT requests."""
        self._handle_request('PUT')

    def do_DELETE(self):
        """Handle DELETE requests."""
        self._handle_request('DELETE')

    def _handle_request(self, method):
        """
        Handle HTTP requests and route them to the appropriate handler.
        """
        try:
            # Check rate limiting
            client_ip = self.client_address[0]
            if is_rate_limited(client_ip):
                self._send_response(error_response('Rate limit exceeded', 429))
                return

            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # Parse request body for POST and PUT requests
            body = None
            if method in ['POST', 'PUT']:
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        body_data = self.rfile.read(content_length)
                        body = parse_json_body(body_data.decode('utf-8'))
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
                    print(f"Client disconnected during request reading: {e}")
                    return
                except Exception as e:
                    print(f"Error parsing request body: {e}")
                    traceback.print_exc()
                    self._send_response(error_response('Invalid request body', 400))
                    return

            # Get authorization header
            auth_header = self.headers.get('Authorization', '')

            # Create request object
            request = {
                'method': method,
                'path': path,
                'query_params': query_params,
                'body': body,
                'headers': dict(self.headers),
                'auth_header': auth_header,
                'client_ip': client_ip,
            }

            # Route the request
            try:
                response = self._route_request(request)
                # Send the response
                self._send_response(response)
            except Exception as e:
                print(f"Error routing request: {e}")
                traceback.print_exc()
                self._send_response(error_response('Internal server error', 500))

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError) as e:
            print(f"Client connection error: {e}")
            # No need to send a response as the client has disconnected
        except Exception as e:
            print(f"Error handling request: {e}")
            traceback.print_exc()
            try:
                self._send_response(error_response('Internal server error', 500))
            except Exception as send_error:
                print(f"Failed to send error response: {send_error}")

    def _route_request(self, request):
        """
        Route the request to the appropriate handler based on the path.
        """
        path = request['path']

        # Auth routes
        if path.startswith('/api/auth/'):
            return handle_auth_routes(request)

        # Device routes
        elif path.startswith('/api/devices'):
            return handle_device_routes(request)

        # Location routes
        elif path.startswith('/api/location/'):
            return handle_location_routes(request)

        # Not found
        else:
            return error_response('Not found', 404)

    def _send_response(self, response):
        """
        Send an HTTP response.
        """
        try:
            self.send_response(response['status'])

            # Set headers
            for header, value in response['headers'].items():
                self.send_header(header, value)

            # Ensure CORS headers are always included
            if 'Access-Control-Allow-Origin' not in response['headers']:
                self.send_header('Access-Control-Allow-Origin', '*')
            if 'Access-Control-Allow-Methods' not in response['headers']:
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            if 'Access-Control-Allow-Headers' not in response['headers']:
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

            self.end_headers()

            # Send body
            if 'body' in response and response['body']:
                try:
                    self.wfile.write(response['body'].encode('utf-8'))
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError) as e:
                    # Client disconnected before we could send the response
                    # This is not a server error, just log it and continue
                    print(f"Client disconnected during response: {e}")
                except Exception as e:
                    print(f"Error sending response body: {e}")
                    traceback.print_exc()
        except Exception as e:
            print(f"Error sending response headers: {e}")
            traceback.print_exc()

class TimeoutHTTPServer(HTTPServer):
    """
    HTTP Server with socket timeout.
    """
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(SERVER_CONFIG['timeout'])
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

def run_server():
    """
    Run the HTTP server.
    """
    try:
        # Create database tables
        create_tables()

        # Start the server
        server_address = (SERVER_CONFIG['host'], SERVER_CONFIG['port'])
        httpd = TimeoutHTTPServer(server_address, RequestHandler)

        print(f"Server running at http://{SERVER_CONFIG['host']}:{SERVER_CONFIG['port']}")
        print(f"Socket timeout set to {SERVER_CONFIG['timeout']} seconds")
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"Error starting server: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    run_server()


