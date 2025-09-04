"""
File: /http/base.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday August 12th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Optional, Dict, Any
from urllib.parse import urljoin
import asyncio
import httpx
from ._http_constants import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_HEADERS

from ..exceptions import LumenError, AuthenticationError, NotFoundError, ValidationError


class BaseHTTPClient:
    """
    Base HTTP client with proper resource management and error handling.
    
    Handles all low-level HTTP operations, connection management, and error handling
    that are common across different API clients.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize base HTTP client.
        
        Args:
            api_key: API key for authentication
        """
        self.base_url = self._normalize_base_url(DEFAULT_BASE_URL)
        self.api_key = api_key
        self.timeout = DEFAULT_TIMEOUT
        self.auto_close = True
        
        self._client = self._create_http_client()

    def __enter__(self):
        """
        Context manager entry point.
        
        Returns:
            Self for use in with statement
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close()
    
    def _create_http_client(self) -> httpx.Client:
        """Create and configure the HTTP client."""
        return httpx.Client(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        """
        Normalize and validate the base URL.
        
        Args:
            base_url: Raw base URL
            
        Returns:
            Normalized base URL
            
        Raises:
            ValueError: If base URL is invalid
        """
        if not base_url:
            raise ValueError("Base URL cannot be empty")
        
        return base_url.rstrip('/')
    
    def close(self):
        """
        Close the HTTP client and clean up resources.
        
        This should be called when the client is no longer needed to prevent
        resource leaks.
        """
        if self._client and not self._client.is_closed:
            self._client.close()

    def __del__(self):
        """
        Destructor to automatically close client when object is garbage collected.
        
        Note: This is a safety net. Proper resource management should use
        explicit close() calls.
        """
        if (hasattr(self, 'auto_close') and self.auto_close and 
            hasattr(self, '_client') and self._client):
            if not self._client.is_closed:
                try:
                    self._client.close()
                except Exception:
                    pass
    
    def _build_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Build request headers including authentication and custom headers.
        
        Args:
            additional_headers: Optional additional headers to include
            
        Returns:
            Dictionary of headers for the request
        """
        headers = DEFAULT_HEADERS.copy()
        
        if self.api_key:
            headers["x-api-key"] = self.api_key
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build the full URL for an API endpoint.
        
        Args:
            endpoint: The API endpoint path
            
        Returns:
            Full URL for the request
        """
        if not endpoint.startswith('/'):
            endpoint = f'/{endpoint}'
        
        return urljoin(f"{self.base_url}/", endpoint.lstrip('/'))
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API with comprehensive error handling.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            json_data: JSON data to send in request body
            params: Query parameters
            headers: Additional headers
            
        Returns:
            Parsed JSON response from the API
            
        Raises:
            AuthenticationError: If authentication fails (401)
            NotFoundError: If resource is not found (404)
            ValidationError: If request validation fails (400)
            LumenError: For other API errors or network issues
        """
        url = self._build_url(endpoint)
        request_headers = self._build_headers(headers)
        
        try:
            response = self._client.request(
                method=method.upper(),
                url=url,
                json=json_data,
                params=params,
                headers=request_headers
            )
            
            self._handle_response_errors(response)
            
            return response.json()
            
        except httpx.TimeoutException as e:
            raise LumenError(f"Request timeout: {str(e)}")
        
        except httpx.RequestError as e:
            raise LumenError(f"Request failed: {str(e)}")
        
        except Exception as e:
            if isinstance(e, (AuthenticationError, NotFoundError, ValidationError, LumenError)):
                raise
            raise LumenError(f"Unexpected error: {str(e)}")
    
    def _handle_response_errors(self, response: httpx.Response):
        """
        Handle HTTP response errors and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
            
        Raises:
            AuthenticationError: For 401 status codes
            NotFoundError: For 404 status codes  
            ValidationError: For 400 status codes
            LumenError: For other 4xx/5xx status codes
        """
        if response.status_code < 400:
            return
        
        error_detail = self._extract_error_detail(response)
        
        if response.status_code == 401:
            raise AuthenticationError(f"Authentication failed: {error_detail}")
        elif response.status_code == 404:
            raise NotFoundError(f"Resource not found: {error_detail}")
        elif response.status_code == 400:
            raise ValidationError(f"Validation error: {error_detail}")
        elif 400 <= response.status_code < 500:
            raise LumenError(f"Client error {response.status_code}: {error_detail}")
        else:
            raise LumenError(f"Server error {response.status_code}: {error_detail}")
    
    def _extract_error_detail(self, response: httpx.Response) -> str:
        """
        Extract error details from HTTP response.
        
        Args:
            response: HTTP response object
            
        Returns:
            Error detail string
        """
        try:
            error_data = response.json()
            return error_data.get("detail", error_data.get("message", str(error_data)))
        except Exception:
            return response.text or f"HTTP {response.status_code}"