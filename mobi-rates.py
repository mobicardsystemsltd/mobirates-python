import json
import base64
import hmac
import hashlib
import random
import requests

class MobicardForexRates:
    def __init__(self, merchant_id, api_key, secret_key):
        self.mobicard_version = "2.0"
        self.mobicard_mode = "TEST"
        self.mobicard_merchant_id = merchant_id
        self.mobicard_api_key = api_key
        self.mobicard_secret_key = secret_key
        self.mobicard_service_id = "20000"
        self.mobicard_service_type = "FOREXRATES"
        self.mobicard_base_currency = "USD"
        
        self.mobicard_token_id = str(random.randint(1000000, 1000000000))
        self.mobicard_txn_reference = str(random.randint(1000000, 1000000000))
    
    def get_forex_rates(self, query_currency=""):
        """Get forex rates for all currencies or specific currency"""
        
        # Create JWT Header
        jwt_header = {"typ": "JWT", "alg": "HS256"}
        encoded_header = base64.urlsafe_b64encode(
            json.dumps(jwt_header).encode()
        ).decode().rstrip('=')
        
        # Create JWT Payload
        jwt_payload = {
            "mobicard_version": self.mobicard_version,
            "mobicard_mode": self.mobicard_mode,
            "mobicard_merchant_id": self.mobicard_merchant_id,
            "mobicard_api_key": self.mobicard_api_key,
            "mobicard_service_id": self.mobicard_service_id,
            "mobicard_service_type": self.mobicard_service_type,
            "mobicard_token_id": self.mobicard_token_id,
            "mobicard_txn_reference": self.mobicard_txn_reference,
            "mobicard_base_currency": self.mobicard_base_currency,
            "mobicard_query_currency": query_currency
        }
        
        encoded_payload = base64.urlsafe_b64encode(
            json.dumps(jwt_payload).encode()
        ).decode().rstrip('=')
        
        # Generate Signature
        header_payload = f"{encoded_header}.{encoded_payload}"
        signature = hmac.new(
            self.mobicard_secret_key.encode(),
            header_payload.encode(),
            hashlib.sha256
        ).digest()
        encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        jwt_token = f"{encoded_header}.{encoded_payload}.{encoded_signature}"
        
        # Make API Call
        url = "https://mobicardsystems.com/api/v1/forex_rates"
        payload = {"mobicard_auth_jwt": jwt_token}
        
        try:
            response = requests.post(url, json=payload, verify=False, timeout=30)
            response_data = response.json()
            
            if response_data.get('status') == 'SUCCESS':
                return {
                    'status': 'SUCCESS',
                    'base_currency': response_data['base_currency'],
                    'timestamp': response_data['timestamp'],
                    'forex_rates': response_data['forex_rates'],
                    'raw_response': response_data
                }
            else:
                return {
                    'status': 'ERROR',
                    'status_code': response_data.get('status_code'),
                    'status_message': response_data.get('status_message')
                }
                
        except Exception as e:
            return {'status': 'ERROR', 'error_message': str(e)}

# Usage
forex_rates = MobicardForexRates(
    merchant_id="4",
    api_key="YmJkOGY0OTZhMTU2ZjVjYTIyYzFhZGQyOWRiMmZjMmE2ZWU3NGIxZWM3ZTBiZSJ9",
    secret_key="NjIwYzEyMDRjNjNjMTdkZTZkMjZhOWNiYjIxNzI2NDQwYzVmNWNiMzRhMzBjYSJ9"
)

# Get all forex rates
result = forex_rates.get_forex_rates()
# Get specific currency rate
# result = forex_rates.get_forex_rates("EUR")

if result['status'] == 'SUCCESS':
    print(f"Base Currency: {result['base_currency']}")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Total Rates Available: {len(result['forex_rates'])}")
    
    # Display sample rates
    print("\nSample Exchange Rates:")
    for i, (pair, rate) in enumerate(result['forex_rates'].items()):
        if i < 5:
            print(f"{pair}: {rate}")
else:
    print(f"Error: {result.get('status_message')}")
