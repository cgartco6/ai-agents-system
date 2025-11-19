import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
import json
import hmac
import hashlib
import base64
from datetime import datetime, timedelta
import logging

class APIIntegrator:
    """Advanced API integration tool with support for multiple authentication methods"""
    
    def __init__(self, base_timeout: int = 30, max_retries: int = 3):
        self.base_timeout = base_timeout
        self.max_retries = max_retries
        self.session = None
        self.api_configs = {}
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logger = logging.getLogger("APIIntegrator")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        """Initialize the API integrator"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.base_timeout)
        )

    async def close(self):
        """Close the API integrator"""
        if self.session:
            await self.session.close()

    def configure_api(self, api_name: str, config: Dict[str, Any]):
        """Configure API connection parameters"""
        self.api_configs[api_name] = config
        self.logger.info(f"Configured API: {api_name}")

    async def make_request(self, api_name: str, endpoint: str, 
                          method: str = 'GET', data: Any = None,
                          params: Dict[str, Any] = None,
                          headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make API request with automatic authentication and error handling"""
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': f"API '{api_name}' not configured"
            }

        config = self.api_configs[api_name]
        url = f"{config['base_url']}{endpoint}"
        
        # Prepare request
        request_headers = await self._prepare_headers(api_name, headers, method, endpoint, data)
        request_params = params or {}
        
        # Make request with retry logic
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                async with self.session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=request_params,
                    json=data if method in ['POST', 'PUT', 'PATCH'] else None,
                    data=data if method not in ['POST', 'PUT', 'PATCH'] else None
                ) as response:
                    
                    response_data = await self._process_response(response)
                    
                    if response.status == 200:
                        self.logger.info(f"Successfully called {api_name} API")
                        return {
                            'status': 'success',
                            'api_name': api_name,
                            'endpoint': endpoint,
                            'method': method,
                            'status_code': response.status,
                            'data': response_data,
                            'headers': dict(response.headers),
                            'retry_attempts': attempt
                        }
                    elif response.status in [429, 500, 502, 503, 504]:  # Retryable errors
                        self.logger.warning(f"Retryable error {response.status} for {api_name}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                    else:
                        return {
                            'status': 'error',
                            'api_name': api_name,
                            'endpoint': endpoint,
                            'method': method,
                            'status_code': response.status,
                            'error': f"HTTP {response.status}: {response_data}",
                            'headers': dict(response.headers)
                        }

            except asyncio.TimeoutError:
                self.logger.error(f"Timeout calling {api_name} API")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return {
                        'status': 'error',
                        'api_name': api_name,
                        'endpoint': endpoint,
                        'method': method,
                        'error': 'Request timeout'
                    }
            except Exception as e:
                self.logger.error(f"Error calling {api_name} API: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                else:
                    return {
                        'status': 'error',
                        'api_name': api_name,
                        'endpoint': endpoint,
                        'method': method,
                        'error': str(e)
                    }

        return {
            'status': 'error',
            'api_name': api_name,
            'endpoint': endpoint,
            'method': method,
            'error': 'Max retries exceeded'
        }

    async def _prepare_headers(self, api_name: str, headers: Dict[str, str], 
                             method: str, endpoint: str, data: Any) -> Dict[str, str]:
        """Prepare request headers with authentication"""
        config = self.api_configs[api_name]
        auth_type = config.get('auth_type', 'none')
        
        # Start with default headers
        request_headers = {
            'User-Agent': 'AIAgentSystem/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Add custom headers
        if headers:
            request_headers.update(headers)
        
        # Apply authentication
        if auth_type == 'api_key':
            request_headers[config['key_header']] = config['api_key']
        elif auth_type == 'bearer_token':
            request_headers['Authorization'] = f"Bearer {config['token']}"
        elif auth_type == 'basic_auth':
            auth_str = f"{config['username']}:{config['password']}"
            encoded_auth = base64.b64encode(auth_str.encode()).decode()
            request_headers['Authorization'] = f"Basic {encoded_auth}"
        elif auth_type == 'oauth2':
            token = await self._get_oauth_token(api_name)
            request_headers['Authorization'] = f"Bearer {token}"
        elif auth_type == 'hmac':
            signature = await self._generate_hmac_signature(api_name, method, endpoint, data)
            request_headers[config['signature_header']] = signature
        
        return request_headers

    async def _get_oauth_token(self, api_name: str) -> str:
        """Get OAuth2 token (simplified implementation)"""
        config = self.api_configs[api_name]
        
        # Check if we have a valid cached token
        if hasattr(self, '_oauth_tokens') and api_name in self._oauth_tokens:
            token_data = self._oauth_tokens[api_name]
            if datetime.now() < token_data['expires_at']:
                return token_data['access_token']
        
        # Get new token
        token_url = config['token_url']
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'scope': config.get('scope', '')
        }
        
        async with self.session.post(token_url, data=token_data) as response:
            if response.status == 200:
                token_response = await response.json()
                access_token = token_response['access_token']
                expires_in = token_response.get('expires_in', 3600)
                
                # Cache the token
                if not hasattr(self, '_oauth_tokens'):
                    self._oauth_tokens = {}
                
                self._oauth_tokens[api_name] = {
                    'access_token': access_token,
                    'expires_at': datetime.now() + timedelta(seconds=expires_in - 60)  # Buffer
                }
                
                return access_token
            else:
                raise Exception(f"Failed to get OAuth token: {response.status}")

    async def _generate_hmac_signature(self, api_name: str, method: str, 
                                     endpoint: str, data: Any) -> str:
        """Generate HMAC signature for authenticated requests"""
        config = self.api_configs[api_name]
        api_secret = config['api_secret']
        
        # Create signature payload
        timestamp = str(int(datetime.now().timestamp()))
        payload_parts = [method.upper(), endpoint, timestamp]
        
        if data:
            if isinstance(data, dict):
                data_str = json.dumps(data, sort_keys=True)
            else:
                data_str = str(data)
            payload_parts.append(data_str)
        
        payload = '|'.join(payload_parts)
        
        # Generate HMAC signature
        signature = hmac.new(
            api_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{config['api_key']}:{timestamp}:{signature}"

    async def _process_response(self, response: aiohttp.ClientResponse) -> Any:
        """Process API response based on content type"""
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            return await response.json()
        elif 'text/' in content_type:
            return await response.text()
        else:
            return await response.read()

    # Specific API integration methods
    async def integrate_openai(self, prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """Integrate with OpenAI API"""
        api_name = 'openai'
        
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': 'OpenAI API not configured'
            }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        return await self.make_request(api_name, '/v1/chat/completions', 'POST', data)

    async def integrate_anthropic(self, prompt: str, model: str = "claude-3-sonnet-20240229") -> Dict[str, Any]:
        """Integrate with Anthropic Claude API"""
        api_name = 'anthropic'
        
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': 'Anthropic API not configured'
            }
        
        data = {
            "model": model,
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        return await self.make_request(api_name, '/v1/messages', 'POST', data)

    async def integrate_payment_gateway(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with payment gateway API"""
        api_name = 'payment_gateway'
        
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': 'Payment gateway API not configured'
            }
        
        return await self.make_request(api_name, '/api/v1/payments', 'POST', payment_data)

    async def integrate_sms_service(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Integrate with SMS service API"""
        api_name = 'sms_service'
        
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': 'SMS service API not configured'
            }
        
        data = {
            "to": phone_number,
            "message": message,
            "from": self.api_configs[api_name].get('sender_id', 'AIAgent')
        }
        
        return await self.make_request(api_name, '/v1/sms', 'POST', data)

    async def integrate_email_service(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with email service API"""
        api_name = 'email_service'
        
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': 'Email service API not configured'
            }
        
        return await self.make_request(api_name, '/v1/send', 'POST', email_data)

    async def integrate_database(self, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Integrate with database API (for cloud databases)"""
        api_name = 'database'
        
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': 'Database API not configured'
            }
        
        data = {
            "query": query,
            "parameters": params or {}
        }
        
        return await self.make_request(api_name, '/query', 'POST', data)

    async def integrate_monitoring(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with monitoring service API"""
        api_name = 'monitoring'
        
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': 'Monitoring API not configured'
            }
        
        return await self.make_request(api_name, '/v1/metrics', 'POST', metrics)

    async def batch_requests(self, api_name: str, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple API requests concurrently"""
        tasks = []
        
        for request in requests:
            task = self.make_request(
                api_name=api_name,
                endpoint=request['endpoint'],
                method=request.get('method', 'GET'),
                data=request.get('data'),
                params=request.get('params'),
                headers=request.get('headers')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'status': 'error',
                    'error': str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results

    async def test_connection(self, api_name: str) -> Dict[str, Any]:
        """Test API connection"""
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': f"API '{api_name}' not configured"
            }
        
        config = self.api_configs[api_name]
        test_endpoint = config.get('test_endpoint', '/health')
        
        result = await self.make_request(api_name, test_endpoint, 'GET')
        
        if result['status'] == 'success':
            return {
                'status': 'success',
                'api_name': api_name,
                'message': 'Connection test passed',
                'response_time': 'measured'  # Would be actual measurement
            }
        else:
            return {
                'status': 'error',
                'api_name': api_name,
                'error': result['error'],
                'suggestion': 'Check API configuration and network connectivity'
            }

    async def get_api_usage_stats(self, api_name: str) -> Dict[str, Any]:
        """Get API usage statistics"""
        # This would track and return usage metrics
        if not hasattr(self, '_usage_stats'):
            self._usage_stats = {}
        
        stats = self._usage_stats.get(api_name, {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0,
            'last_request': None
        })
        
        return {
            'api_name': api_name,
            'statistics': stats,
            'rate_limits': self.api_configs[api_name].get('rate_limits', 'Unknown')
        }

    async def validate_api_response(self, response: Dict[str, Any], 
                                  validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API response against rules"""
        errors = []
        data = response.get('data', {})
        
        for field, rules in validation_rules.items():
            if field not in data:
                if rules.get('required', False):
                    errors.append(f"Missing required field: {field}")
                continue
            
            value = data[field]
            
            # Type validation
            expected_type = rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                errors.append(f"Field {field} should be {expected_type}, got {type(value)}")
            
            # Value validation
            if 'min_length' in rules and len(str(value)) < rules['min_length']:
                errors.append(f"Field {field} too short (min {rules['min_length']})")
            
            if 'max_length' in rules and len(str(value)) > rules['max_length']:
                errors.append(f"Field {field} too long (max {rules['max_length']})")
            
            if 'pattern' in rules and not re.match(rules['pattern'], str(value)):
                errors.append(f"Field {field} doesn't match pattern")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'validated_fields': len(validation_rules)
        }

    async def transform_api_data(self, data: Any, transformation_rules: Dict[str, Any]) -> Any:
        """Transform API data according to rules"""
        if isinstance(data, dict):
            transformed = {}
            for key, value in data.items():
                if key in transformation_rules:
                    rule = transformation_rules[key]
                    if rule.get('type') == 'rename':
                        new_key = rule['new_name']
                        transformed[new_key] = value
                    elif rule.get('type') == 'transform':
                        transform_func = rule['function']
                        transformed[key] = await self._apply_transform(value, transform_func)
                    else:
                        transformed[key] = value
                else:
                    transformed[key] = value
            return transformed
        elif isinstance(data, list):
            return [await self.transform_api_data(item, transformation_rules) for item in data]
        else:
            return data

    async def _apply_transform(self, value: Any, transform_func: str) -> Any:
        """Apply transformation function to value"""
        try:
            if transform_func == 'to_upper':
                return str(value).upper()
            elif transform_func == 'to_lower':
                return str(value).lower()
            elif transform_func == 'parse_date':
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif transform_func == 'format_currency':
                return f"${float(value):.2f}"
            else:
                return value
        except:
            return value

    async def create_api_documentation(self, api_name: str) -> Dict[str, Any]:
        """Generate API documentation from configuration"""
        if api_name not in self.api_configs:
            return {
                'status': 'error',
                'error': f"API '{api_name}' not configured"
            }
        
        config = self.api_configs[api_name]
        
        documentation = {
            'api_name': api_name,
            'base_url': config['base_url'],
            'authentication': {
                'type': config.get('auth_type', 'none'),
                'description': self._get_auth_description(config.get('auth_type'))
            },
            'rate_limits': config.get('rate_limits', 'Not specified'),
            'endpoints': config.get('documented_endpoints', []),
            'configuration_date': datetime.now().isoformat()
        }
        
        return documentation

    def _get_auth_description(self, auth_type: str) -> str:
        """Get authentication method description"""
        descriptions = {
            'api_key': 'API Key in header',
            'bearer_token': 'Bearer token authentication',
            'basic_auth': 'Basic username/password authentication',
            'oauth2': 'OAuth 2.0 token authentication',
            'hmac': 'HMAC signature authentication',
            'none': 'No authentication required'
        }
        return descriptions.get(auth_type, 'Unknown authentication method')
