import pytest
import threading
import socketserver
import time
import sys
import os

# Dynamically add the root workspace directory to sys.path to import the prototype mock server
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(root_dir)

from server import ImeiApiPrototypeHandler

@pytest.fixture(scope="session")
def server_url():
    """
    Spins up the official prototype mock server in a background thread
    on port 8001 for real integration testing of the SDK.
    """
    class TestTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    PORT = 8001
    
    # Overwrite the Handler to serve static files and API endpoints using proper RFC HTTP protocol ordering
    class RelativeImeiApiPrototypeHandler(ImeiApiPrototypeHandler):
        def serve_file(self, file_path, content_type):
            full_path = os.path.join(root_dir, file_path)
            if not os.path.exists(full_path):
                self.send_error(404, f"Plik {full_path} nie został odnaleziony.")
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            with open(full_path, "rb") as f:
                self.wfile.write(f.read())

        def send_response_headers_cors(self):
            # Overridden to do nothing here because we want to send headers AFTER send_response
            pass

        def send_real_headers(self, status_code: int):
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
            self.end_headers()

        def handle_api_services(self):
            import json
            
            auth_header = self.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                self.send_real_headers(401)
                error_resp = {
                    "error": "Unauthorized",
                    "code": "missing_api_key",
                    "message": "Missing or invalid API key. Please pass 'Authorization: Bearer <your_token>' header."
                }
                self.wfile.write(json.dumps(error_resp, indent=2).encode("utf-8"))
                return

            self.send_real_headers(200)
            mock_services = [
                {
                    "id": 0,
                    "name": "Basic IMEI Check",
                    "price": "Token based"
                },
                {
                    "id": 86,
                    "name": "GENERIC: Xiaomi Mi Lock Info Check",
                    "price": 0.02
                },
                {
                    "id": 72,
                    "name": "GENERIC: Oppo Info Check",
                    "price": 0.60
                },
                {
                    "id": 120,
                    "name": "APPLE: iPhone Carrier & Blacklist Info",
                    "price": 0.15
                }
            ]
            self.wfile.write(json.dumps(mock_services, indent=2).encode("utf-8"))

        def handle_api_history(self, path):
            import json
            
            auth_header = self.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                self.send_real_headers(401)
                error_resp = {
                    "error": "Unauthorized",
                    "code": "missing_api_key",
                    "message": "Missing or invalid API key. Please pass 'Authorization: Bearer <your_token>' header."
                }
                self.wfile.write(json.dumps(error_resp, indent=2).encode("utf-8"))
                return

            parts = [p for p in path.split("/") if p]
            history_id = 0
            try:
                history_id = int(parts[-1])
            except ValueError:
                pass

            self.send_real_headers(200)
            mock_history = {
                "id": history_id,
                "status": "Done",
                "service": "Basic IMEI Check",
                "token_request_price": "0.00",
                "result": {
                    "imei": "353541326469521",
                    "brand": "Apple",
                    "model": "iPhone 12 Pro Max",
                    "tac": "35354132",
                    "blacklist_status": "CLEAN",
                    "carrier_lock": False,
                    "original_carrier": "T-Mobile Polska",
                    "purchase_country": "Poland",
                    "specifications": {
                        "cpu": "Apple A14 Bionic",
                        "ram_gb": 6,
                        "storage_gb": 128,
                        "screen_size": "6.7 inches"
                    }
                }
            }
            self.wfile.write(json.dumps(mock_history, indent=2).encode("utf-8"))

        def handle_api_mock(self, query_params):
            import json
            
            # A. Verify Authorization header
            auth_header = self.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                self.send_real_headers(401)
                error_resp = {
                    "error": "Unauthorized",
                    "code": "missing_api_key",
                    "message": "Missing or invalid API key. Please pass 'Authorization: Bearer <your_token>' header."
                }
                self.wfile.write(json.dumps(error_resp, indent=2).encode("utf-8"))
                return

            # B. Read IMEI from query params
            imei_list = query_params.get("imei")
            if not imei_list:
                self.send_real_headers(400)
                error_resp = {
                    "error": "Bad Request",
                    "code": "missing_imei_param",
                    "message": "Query parameter 'imei' is required."
                }
                self.wfile.write(json.dumps(error_resp, indent=2).encode("utf-8"))
                return

            imei = imei_list[0]

            # C. Logika mockowania w zależności od numeru IMEI
            if imei == "353541326469521":
                self.send_real_headers(200)
                success_resp = {
                    "imei": imei,
                    "brand": "Apple",
                    "model": "iPhone 12 Pro Max",
                    "tac": "35354132",
                    "blacklist_status": "CLEAN",
                    "carrier_lock": False,
                    "original_carrier": "T-Mobile Polska",
                    "purchase_country": "Poland",
                    "specifications": {
                        "cpu": "Apple A14 Bionic",
                        "ram_gb": 6,
                        "storage_gb": 128,
                        "screen_size": "6.7 inches"
                    }
                }
                self.wfile.write(json.dumps(success_resp, indent=2).encode("utf-8"))

            elif imei == "350545260771498":
                self.send_real_headers(200)
                success_resp = {
                    "imei": imei,
                    "brand": "Samsung",
                    "model": "Galaxy S24 Ultra",
                    "tac": "35054526",
                    "blacklist_status": "CLEAN",
                    "carrier_lock": False,
                    "original_carrier": "Orange Polska",
                    "purchase_country": "Poland",
                    "specifications": {
                        "cpu": "Snapdragon 8 Gen 3",
                        "ram_gb": 12,
                        "storage_gb": 256,
                        "screen_size": "6.8 inches"
                    }
                }
                self.wfile.write(json.dumps(success_resp, indent=2).encode("utf-8"))

            elif imei == "355030794352540":
                self.send_real_headers(200)
                blacklist_resp = {
                    "imei": imei,
                    "brand": "Google",
                    "model": "Pixel 8 Pro",
                    "tac": "35503079",
                    "blacklist_status": "BLACKLISTED",
                    "carrier_lock": True,
                    "original_carrier": "T-Mobile USA",
                    "purchase_country": "United States",
                    "specifications": {
                        "cpu": "Google Tensor G3",
                        "ram_gb": 12,
                        "storage_gb": 128,
                        "screen_size": "6.7 inches"
                    }
                }
                self.wfile.write(json.dumps(blacklist_resp, indent=2).encode("utf-8"))

            elif imei == "353541326469529":
                self.send_real_headers(422)
                error_resp = {
                    "error": "Unprocessable Entity",
                    "code": "invalid_luhn_checksum",
                    "message": f"Luhn checksum for IMEI '{imei}' is invalid. Make sure the IMEI is 15 digits long and has a valid check digit."
                }
                self.wfile.write(json.dumps(error_resp, indent=2).encode("utf-8"))

            else:
                self.send_real_headers(402)
                error_resp = {
                    "error": "Payment Required",
                    "code": "insufficient_credits",
                    "message": f"Your API balance is $0.00. Please recharge your account in the developer dashboard at dash.imei.info before executing queries."
                }
                self.wfile.write(json.dumps(error_resp, indent=2).encode("utf-8"))

    handler = RelativeImeiApiPrototypeHandler
    httpd = TestTCPServer(("", PORT), handler)
    
    # Start server in a background daemon thread
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    
    # Give the background server a moment to bind and boot up
    time.sleep(0.3)
    
    yield f"http://localhost:{PORT}"
    
    # Shutdown and clean up the server after the test session finishes
    httpd.shutdown()
    httpd.server_close()
    thread.join()
