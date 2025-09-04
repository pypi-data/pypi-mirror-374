"""
File: /tool_function.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday August 12th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Optional, Dict, Any

from .exceptions.exceptions import LumenError


class ToolFunction:
    """
    Callable tool function with schema information and execution capabilities.
    
    This class wraps individual API actions into callable functions that can be
    executed directly with proper error handling and parameter validation.
    
    Example:
        tool_function = ToolFunction(client, user_id, action, connection_id, schema)
        result = await tool_function(subject="Hello", body="World")
    """
    
    def __init__(
        self,
        client,
        user_id: str,
        action: str,
        connection_id: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize tool function.
        
        Args:
            client: LumenClient instance for API communication
            user_id: User ID for execution context
            action: Action constant for this function
            connection_id: Optional connection ID
            schema: Optional schema information for the function
        """
        self.client = client
        self.user_id = user_id
        self.action = action
        self.connection_id = connection_id
        self.schema = schema
        
        # Cache metadata for performance
        self._metadata = None
        self._provider = None
        self._service = None
        self._friendly_name = None
    
    @property
    def metadata(self) -> Dict[str, str]:
        """Get cached metadata for this action."""
        if self._metadata is None:
            self._metadata = self.client.tools.get_action_metadata(self.action)
        return self._metadata
    
    @property
    def provider(self) -> str:
        """Get provider name for this action."""
        if self._provider is None:
            self._provider = self.metadata["provider"]
        return self._provider
    
    @property
    def service(self) -> str:
        """Get service name for this action."""
        if self._service is None:
            self._service = self.metadata["service"]
        return self._service
    
    @property
    def friendly_name(self) -> str:
        """Get friendly name for this action."""
        if self._friendly_name is None:
            self._friendly_name = self.metadata["friendly_name"]
        return self._friendly_name
    
    async def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool function with the provided arguments.
        
        This method validates inputs, prepares the API payload, and executes
        the action with comprehensive error handling.
        
        Args:
            **kwargs: Arguments to pass to the tool function
            
        Returns:
            Dictionary containing the execution result
            
        Raises:
            ValueError: If arguments are invalid
            LumenError: If tool execution fails
        """
        # Validate execution context
        self._validate_execution_context()
        
        # Prepare execution payload
        payload = self._build_execution_payload(kwargs)
        
        # Execute the action
        try:
            return await self.client._make_request(
                method="POST",
                endpoint=f"/actions/{self.friendly_name}",
                json_data=payload
            )
        except Exception as e:
            raise LumenError(
                f"Failed to execute {self.friendly_name} "
                f"({self.provider}.{self.service}): {str(e)}"
            )
    
    def get_schema(self) -> Optional[Dict[str, Any]]:
        """
        Get the complete schema for this tool function.
        
        Returns:
            Dictionary containing the schema, or None if not available
        """
        return self.schema
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get the parameters schema for this tool function.
        
        Returns:
            Dictionary containing parameter definitions, or empty dict if schema not available
        """
        if not self.schema:
            return {}
        
        return self.schema.get("parameters", {})
    
    def get_description(self) -> str:
        """
        Get the description for this tool function.
        
        Returns:
            String description, or default message if not available
        """
        if self.schema and "description" in self.schema:
            return self.schema["description"]
        
        return f"{self.provider} {self.service} action: {self.action}"
    
    def get_parameter_info(self, parameter_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific parameter.
        
        Args:
            parameter_name: Name of the parameter to get info for
            
        Returns:
            Dictionary with parameter information, or None if not found
        """
        parameters = self.get_parameters()
        properties = parameters.get("properties", {})
        
        return properties.get(parameter_name)
    
    def get_required_parameters(self) -> list[str]:
        """
        Get list of required parameter names.
        
        Returns:
            List of required parameter names
        """
        parameters = self.get_parameters()
        return parameters.get("required", [])
    
    def validate_parameters(self, **kwargs) -> Dict[str, str]:
        """
        Validate provided parameters against schema.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            Dictionary of validation errors (empty if no errors)
        """
        errors = {}
        parameters = self.get_parameters()
        
        if not parameters:
            return errors
        
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])
        
        # Check required parameters
        for req_param in required:
            if req_param not in kwargs:
                errors[req_param] = f"Required parameter '{req_param}' is missing"
        
        # Check parameter types and constraints
        for param_name, param_value in kwargs.items():
            if param_name in properties:
                param_schema = properties[param_name]
                param_errors = self._validate_single_parameter(
                    param_name, param_value, param_schema
                )
                if param_errors:
                    errors[param_name] = param_errors
        
        return errors
    
    def __repr__(self) -> str:
        """String representation of the tool function."""
        return (
            f"ToolFunction(action='{self.action}', "
            f"provider='{self.provider}', "
            f"service='{self.service}', "
            f"user_id='{self.user_id}')"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.provider}.{self.service}.{self.friendly_name}({self.user_id})"
    
    def _validate_execution_context(self) -> None:
        """
        Validate that the function has all necessary context for execution.
        
        Raises:
            ValueError: If execution context is invalid
        """
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty for function execution")
        
        if not self.action:
            raise ValueError("Action cannot be empty")
        
        try:
            _ = self.metadata
        except Exception as e:
            raise ValueError(f"Invalid action for function execution: {str(e)}")
    
    def _build_execution_payload(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the execution payload for the API request.
        
        Args:
            kwargs: Function arguments
            
        Returns:
            Dictionary containing the API payload
        """
        return {
            "user_id": self.user_id.strip(),
            "provider": self.provider,
            "service": self.service,
            "parameters": kwargs
        }
    
    def _validate_single_parameter(
        self, 
        param_name: str, 
        param_value: Any, 
        param_schema: Dict[str, Any]
    ) -> Optional[str]:
        """
        Validate a single parameter against its schema.
        
        Args:
            param_name: Name of the parameter
            param_value: Value to validate
            param_schema: Schema for the parameter
            
        Returns:
            Error message if validation fails, None otherwise
        """
        param_type = param_schema.get("type")
        
        if param_type == "string" and not isinstance(param_value, str):
            return f"Parameter '{param_name}' must be a string"
        elif param_type == "integer" and not isinstance(param_value, int):
            return f"Parameter '{param_name}' must be an integer"
        elif param_type == "boolean" and not isinstance(param_value, bool):
            return f"Parameter '{param_name}' must be a boolean"
        elif param_type == "array" and not isinstance(param_value, list):
            return f"Parameter '{param_name}' must be an array"
        elif param_type == "object" and not isinstance(param_value, dict):
            return f"Parameter '{param_name}' must be an object"
        
        return None