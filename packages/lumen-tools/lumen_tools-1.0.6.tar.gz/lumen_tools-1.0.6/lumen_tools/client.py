"""
File: /client.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Wednesday September 3rd 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Optional, Dict, Any

from lumen_tools.constants import NO_AUTH_PROVIDERS

from .http import BaseHTTPClient
from .managers import ToolsManager, ProviderManager, TriggersManager
from .models import ConnectionCreate, ConnectionResponse, ProviderCredentials


class LumenClient(BaseHTTPClient):
    """
    Main client for interacting with Lumen Core API.
    
    This client handles HTTP requests, authentication, and error handling
    for all Lumen Core API interactions with a focus on reliability and maintainability.
    
    Example:
        async with LumenClient(api_key="your_key") as client:
            user = client.get_entity("user123")
            connection = client.connect_provider("user123", "google", credentials)
    """
    
    def __init__(self, api_key: Optional[str] = None, provider: Optional[Any] = None):
        """
        Initialize Lumen Core client.
        
        Args:
            api_key: API key for authentication.
            provider: Provider instance for framework-specific integrations (e.g., LangchainProvider)
        """
        super().__init__(api_key=api_key)
        
        self.tools = ToolsManager(self, provider=provider)
        self.provider = ProviderManager(self)  
        self.triggers = TriggersManager(self)
        self._framework_provider = provider
    
    def connect_provider(
        self,
        user_id: str,
        provider_name: str,
        credentials: Optional[ProviderCredentials] = None,
        scopes: Optional[str] = None
    ) -> ConnectionResponse:
        """
        Connect a single provider for a user with specified scopes and get OAuth URL.

        This method automatically creates the connection and generates the OAuth 
        authorization URL for OAuth providers, directly connects API key providers,
        or connects no-auth providers without credentials.

        Args:
            user_id: The unique identifier for the user
            provider_name: Name of the provider (e.g., 'google', 'serpapi', 'firecrawl', 'hackernews')
            credentials: Provider credentials object (optional for no-auth providers)
            scopes: Optional service scope as string (e.g., 'gmail') - not needed for API key or no-auth providers
            
        Returns:
            ConnectionResponse with connection details and OAuth URL (for OAuth providers only)
            
        Raises:
            ValueError: If required parameters are invalid
            LumenError: For API errors
        """
        self._validate_user_id(user_id)
        self._validate_provider_name(provider_name)
        
        user_id = user_id.strip()
        provider_name = provider_name.strip().lower()
        
        self.__get_entity(user_id)
        
        if provider_name in NO_AUTH_PROVIDERS:
            if credentials is not None:
                print(f"Warning: Provider '{provider_name}' doesn't require credentials. Ignoring provided credentials.")
            credentials = ProviderCredentials(services=[])
        else:
            self._validate_credentials(credentials)
        
        credentials_dict = self._prepare_credentials_dict(credentials, scopes)
        updated_credentials = ProviderCredentials(**credentials_dict)
        
        providers = {provider_name: updated_credentials}
        connection_response = self.__create_connection(user_id, providers)
        
        if scopes and credentials and not credentials.api_key and provider_name not in NO_AUTH_PROVIDERS:
            self._add_oauth_url_to_response(
                connection_response, provider_name, scopes, user_id
            )
        
        return connection_response
    
    def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """
        Handle OAuth callback with authorization code and state.
        
        Args:
            code: Authorization code from OAuth provider
            state: State parameter to verify the request
            
        Returns:
            Dictionary containing callback result with provider, service, status, and tokens
            
        Raises:
            ValueError: If code or state is empty
            ValidationError: If state is invalid or callback fails
            LumenError: For other API errors
            
        Example:
            result = client.handle_oauth_callback(
                code="authorization_code_from_callback",
                state="state_from_callback"
            )
            print(f"Authentication status: {result['status']}")
        """
        self._validate_oauth_params(code, state)
        
        return self._make_request(
            method="GET",
            endpoint="/oauth/callback",
            params={
                "code": code.strip(),
                "state": state.strip()
            }
        )

    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID parameter."""
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

    def _validate_provider_name(self, provider_name: str) -> None:
        """Validate provider name parameter."""
        if not provider_name or not provider_name.strip():
            raise ValueError("Provider name cannot be empty")

    def _validate_credentials(self, credentials: Optional[ProviderCredentials]) -> None:
        """Validate credentials parameter for OAuth and API key providers."""
        if not credentials:
            raise ValueError("Credentials cannot be empty for authenticated providers")
        
        # Check if it's an API key provider
        if credentials.api_key:
            if not credentials.api_key.strip():
                raise ValueError("API key cannot be empty")
            return
        
        # OAuth provider validation
        if not credentials.client_id or not credentials.client_secret:
            raise ValueError("Client ID and client secret are required for OAuth providers")

    def _validate_providers(self, providers: Dict[str, ProviderCredentials]) -> None:
        """Validate providers dictionary."""
        if not providers:
            raise ValueError("Providers dictionary cannot be empty")

    def _validate_connection_id(self, connection_id: str) -> None:
        """Validate connection ID parameter."""
        if not connection_id or not connection_id.strip():
            raise ValueError("Connection ID cannot be empty")

    def _validate_oauth_params(self, code: str, state: str) -> None:
        """Validate OAuth callback parameters."""
        if not code or not code.strip():
            raise ValueError("Authorization code cannot be empty")
        if not state or not state.strip():
            raise ValueError("State parameter cannot be empty")

    def _prepare_credentials_dict(
        self, 
        credentials: Optional[ProviderCredentials], 
        scopes: Optional[str]
    ) -> Dict[str, Any]:
        """Prepare credentials dictionary with scopes for OAuth, API key, and no-auth providers."""
        if credentials is None:
            return {'services': []}
        
        if isinstance(credentials, ProviderCredentials):
            credentials_dict = credentials.model_dump()
        else:
            credentials_dict = credentials.copy() if hasattr(credentials, 'copy') else dict(credentials)
        
        if credentials_dict.get('api_key'):
            credentials_dict.pop('services', None)
            return credentials_dict
        
        if scopes:
            credentials_dict['services'] = [scopes]
        elif 'services' not in credentials_dict or not credentials_dict['services']:
            credentials_dict['services'] = []
        
        return credentials_dict

    def _serialize_providers(self, providers: Dict[str, ProviderCredentials]) -> Dict[str, Any]:
        """Serialize providers dictionary for API request."""
        return {
            provider_name: (
                creds.model_dump() if isinstance(creds, ProviderCredentials) else creds
            )
            for provider_name, creds in providers.items()
        }

    def _add_oauth_url_to_response(
        self,
        connection_response: ConnectionResponse,
        provider_name: str,
        service: str,
        user_id: str
    ) -> None:
        """Add OAuth URL to connection response if possible (OAuth providers only)."""
        try:
            if not service:
                print(f"Skipping OAuth URL generation for API key provider: {provider_name}")
                return
                
            if provider_name in NO_AUTH_PROVIDERS:
                print(f"Skipping OAuth URL generation for no-auth provider: {provider_name}")
                return
                
            auth_response = self._get_oauth_authorization_url(
                connection_id=connection_response.connection_id,
                provider=provider_name,
                service=service,
                user_id=user_id
            )
            
            connection_response.redirect_url = auth_response.get("auth_url")
            connection_response.state = auth_response.get("state")
        except Exception as e:
            print(f"Warning: Could not generate OAuth URL: {str(e)}")

    def _get_oauth_authorization_url(
        self,
        connection_id: str,
        provider: str,
        service: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Internal method to get OAuth authorization URL from the API.
        
        Args:
            connection_id: The connection ID
            provider: Provider name
            service: Service name  
            user_id: User ID
            
        Returns:
            Dictionary with redirect_url and state
        """
        return self._make_request(
            method="GET",
            endpoint=f"/oauth/{connection_id}/{provider}/{service}/authorize",
            params={"user_id": user_id}
        )
    
    def __get_entity(self, user_id: str) -> Dict[str, Any]:
        """
        Create or retrieve a user by ID.
        
        This method automatically handles user creation if the user doesn't exist,
        so developers don't need to worry about whether a user exists or not.
        
        Args:
            user_id: The unique identifier for the user
            
        Returns:
            Dictionary containing user data from the API response
            
        Raises:
            ValueError: If user_id is empty or invalid
            AuthenticationError: If API key is invalid
            ValidationError: If user_id format is invalid
            LumenError: For other API errors
        """
        self._validate_user_id(user_id)
        
        return self._make_request(
            method="POST",
            endpoint="/users/",
            params={"uniqueUserId": user_id.strip()}
        )
    
    def __create_connection(
        self,
        user_id: str,
        providers: Dict[str, ProviderCredentials]
    ) -> ConnectionResponse:
        """
        Create a unified connection supporting multiple providers and services.
        
        This is the legacy method that supports multiple providers at once.
        For simpler use cases, consider using connect_provider() instead.
        
        Args:
            user_id: The unique identifier for the user
            providers: Dictionary of provider configurations
                     Key: provider name (e.g., 'google')
                     Value: ProviderCredentials object with client_id, client_secret, services, callback_url
        
        Returns:
            ConnectionResponse object containing connection details
            
        Raises:
            ValueError: If user_id is empty or providers is empty
            ValidationError: If provider/service combination is invalid
            LumenError: For other API errors
        """
        self._validate_user_id(user_id)
        self._validate_providers(providers)
        
        providers_dict = self._serialize_providers(providers)
        
        connection_data = ConnectionCreate(
            user_id=user_id.strip(),
            providers=providers_dict
        )
        
        response_data = self._make_request(
            method="POST",
            endpoint="/connections/",
            json_data=connection_data.model_dump()
        )
        
        return ConnectionResponse(**response_data)