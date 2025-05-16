from http.server import BaseHTTPRequestHandler
from backend.routes.auth import handle_auth_routes
from backend.routes.devices import handle_device_routes
from backend.routes.locations import handle_location_routes
from backend.utils.http import error_response, parse_json_body
import json
from urllib.parse import urlparse, parse_qs

class VercelHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle preflight requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')  # 24 hours
        self.end_headers()

    def do_GET(self):
        self._handle_request('GET')

    def do_POST(self):
        self._handle_request('POST')

    def do_PUT(self):
        self._handle_request('PUT')

    def do_DELETE(self):
        self._handle_request('DELETE')

    def _handle_request(self, method):
        try:
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)

            # Parse request body for POST and PUT requests
            body = None
            if method in ['POST', 'PUT']:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    body_data = self.rfile.read(content_length)
                    body = parse_json_body(body_data.decode('utf-8'))

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
                'client_ip': self.client_address[0] if hasattr(self, 'client_address') else '0.0.0.0',
            }

            # Route the request
            response = self._route_request(request)

            # Send the response
            self._send_response(response)
        except Exception as e:
            import traceback
            error_msg = f"Internal Server Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)  # This will show in Vercel logs
            self._send_response(error_response(str(e), 500))

    def _route_request(self, request):
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
        try:
            self.send_response(response['status'])

            # Set headers
            for key, value in response.get('headers', {}).items():
                self.send_header(key, value)

            # Set default headers if not present
            if 'Content-Type' not in response.get('headers', {}):
                self.send_header('Content-Type', 'application/json')

            # Add CORS headers
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

            self.end_headers()

            # Send body
            if 'body' in response and response['body']:
                response_data = json.dumps(response['body']).encode('utf-8')
                self.wfile.write(response_data)
        except Exception as e:
            print(f"Error sending response: {str(e)}")
            # If we can't send the proper response, try to send a basic error
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_data = json.dumps({'error': 'Internal Server Error'}).encode('utf-8')
                self.wfile.write(error_data)
            except:
                pass  # At this point, we can't do anything else

def handler(request, context):
    """
    Serverless function handler for Vercel.
    """
    try:
        # Extract request information
        method = request.get('method', '')
        path = request.get('path', '')
        headers = request.get('headers', {})
        body = request.get('body', None)

        # Handle CORS preflight requests
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }

        # Create request object
        api_request = {
            'method': method,
            'path': path,
            'query_params': request.get('query', {}),
            'body': body,
            'headers': headers,
            'auth_header': headers.get('authorization', ''),
            'client_ip': headers.get('x-forwarded-for', '0.0.0.0'),
        }

        # Log request information for debugging
        print(f"Processing request: {method} {path}")

        # Route the request based on path
        try:
            if path.startswith('/api/auth/'):
                response = handle_auth_routes(api_request)
            elif path.startswith('/api/devices'):
                response = handle_device_routes(api_request)
            elif path.startswith('/api/location/'):
                response = handle_location_routes(api_request)
            else:
                response = error_response('Not found', 404)

            # Convert response format for Vercel
            return {
                'statusCode': response['status'],
                'headers': response.get('headers', {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                }),
                'body': response.get('body', '')
            }

        except Exception as route_error:
            # Log the specific routing error
            error_message = f"Error in route handler: {str(route_error)}"
            print(error_message)
            import traceback
            print(traceback.format_exc())

            error_resp = error_response(error_message, 500)
            return {
                'statusCode': error_resp['status'],
                'headers': error_resp.get('headers', {'Content-Type': 'application/json'}),
                'body': error_resp.get('body', '')
            }

    except Exception as e:
        # Log the general error
        error_message = f"Unhandled server error: {str(e)}"
        print(error_message)
        import traceback
        print(traceback.format_exc())

        error_resp = error_response(error_message, 500)
        return {
            'statusCode': error_resp['status'],
            'headers': error_resp.get('headers', {'Content-Type': 'application/json'}),
            'body': error_resp.get('body', '')
        }