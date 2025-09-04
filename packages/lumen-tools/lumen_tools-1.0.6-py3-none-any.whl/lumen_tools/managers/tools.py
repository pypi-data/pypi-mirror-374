"""
File: /managers/tools.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Wednesday September 3rd 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Optional, Dict, Any, List, Union, overload
from openai.types.chat import ChatCompletionToolParam
from langchain.tools import BaseTool, StructuredTool

from lumen_tools.constants import ACTION_METADATA
from ..tool_function import ToolFunction


class ToolsManager:
    """
    Manager for tool-related operations including schema retrieval and function creation.
    
    This manager handles the complex logic of converting action constants to callable
    tool functions and managing tool schemas for OpenAI and Langchain integration.
    """
    
    FRIENDLY_NAME_TO_ACTION = {
        metadata["friendly_name"]: action 
        for action, metadata in ACTION_METADATA.items()
    }

    def __init__(self, client, provider: Optional[Any] = None):
        """
        Initialize tools manager.
        
        Args:
            client: LumenClient instance for API communication
            provider: Optional framework provider (e.g., LangchainProvider)
        """
        self.client = client
        if provider and hasattr(provider, 'provider_type') and provider.provider_type == "langchain":
            if not hasattr(provider, 'client') or provider.client is None:
                provider.client = client
        
        self._framework_provider = provider

    def get_action_metadata(self, action: str) -> Dict[str, str]:
        """
        Get metadata for an action constant.
        
        Args:
            action: Action constant (e.g., Action.GMAIL_SEND_EMAIL)
            
        Returns:
            Dictionary with provider, service, and friendly_name
            
        Raises:
            ValueError: If action is not found
        """
        if action not in ACTION_METADATA:
            available_actions = list(ACTION_METADATA.keys())[:5]
            raise ValueError(
                f"Unknown action: {action}. "
                f"Available actions include: {available_actions}..."
            )
        
        return ACTION_METADATA[action].copy()
    
    @overload
    def get(self, user_id: str, tools: Optional[List[str]] = None) -> List[ChatCompletionToolParam]:
        ...

    @overload  
    def get(self, user_id: str, tools: Optional[List[str]] = None) -> List[BaseTool]:
        ...

    def get(self, user_id: str, tools: Optional[List[str]] = None):
        """
        Get tool schemas from action constants or app constants.
        Automatically detects provider type and returns appropriate format.
        
        Args:
            user_id: User ID to fetch user-specific available actions when tools is None
            tools: List of action constants (e.g., [Action.GMAIL_SEND_EMAIL])
                or app constants (e.g., [App.GMAIL, App.DRIVE])
                or None to get all available tools
                
        Returns:
            List of ChatCompletionToolParam objects for OpenAI integration
            OR List of BaseTool objects for Langchain integration
            
        Raises:
            ValueError: If tools parameter is invalid
            LumenError: If schema retrieval fails
        """
        is_langchain = (self._framework_provider and 
                       hasattr(self._framework_provider, 'provider_type') and 
                       self._framework_provider.provider_type == "langchain")
        
        if is_langchain:
            return self._get_langchain_tools(user_id, tools)
        else:
            return self._get_openai_tools(user_id, tools)

    def _get_openai_tools(self, user_id: str, tools: Optional[List[str]] = None) -> List[ChatCompletionToolParam]:
        """Get tools formatted for OpenAI integration."""
        from lumen_tools.constants import APP_TO_ACTIONS
        
        if tools is None:
            if user_id:
                return self._get_user_available_actions_openai(user_id)
        else:
            validated_tools = self._validate_and_prepare_tools(tools)
    
        tool_schemas: List[ChatCompletionToolParam] = []
        processed_providers = set()
        
        for tool in validated_tools:
            if tool in APP_TO_ACTIONS:
                self._process_app_constant_openai(tool, user_id, tool_schemas, processed_providers)
            else:
                self._process_action_constant_openai(tool, tool_schemas)
        
        if not tool_schemas:
            raise ValueError("No valid tool schemas could be retrieved")
        
        return tool_schemas

    def _get_langchain_tools(self, user_id: str, tools: Optional[List[str]] = None) -> List[BaseTool]:
        """Get tools formatted for Langchain integration."""
        from lumen_tools.constants import APP_TO_ACTIONS
        
        if tools is None:
            if user_id:
                return self._get_user_available_actions_langchain(user_id)
        else:
            validated_tools = self._validate_and_prepare_tools(tools)

        langchain_tools: List[BaseTool] = []
        processed_providers = set()
        
        for tool in validated_tools:
            if tool in APP_TO_ACTIONS:
                self._process_app_constant_langchain(tool, user_id, langchain_tools, processed_providers)
            else:
                self._process_action_constant_langchain(tool, langchain_tools, user_id)
        
        if not langchain_tools:
            raise ValueError("No valid tool schemas could be retrieved")
        
        return langchain_tools

    def _get_user_available_actions_openai(self, user_id: str) -> List[ChatCompletionToolParam]:
        """
        Get all available actions for a specific user based on their authenticated connections (OpenAI format).
        
        Args:
            user_id: User ID to fetch available actions for
            
        Returns:
            List of ChatCompletionToolParam objects for user's available actions
            
        Raises:
            LumenError: If API request fails
        """
        try:
            available_actions = self.client._make_request(
                method="GET",
                endpoint="/actions/",
                params={"user_id": user_id}
            )
            
            tool_schemas: List[ChatCompletionToolParam] = []
            
            for action in available_actions:
                if isinstance(action, dict) and "function" in action:
                    schema = {"type": "function", "function": action["function"]}
                elif isinstance(action, dict):
                    schema = {"type": "function", "function": action}
                else:
                    continue
                
                try:
                    tool_schemas.append(ChatCompletionToolParam(**schema))
                except Exception as e:
                    print(f"Warning: Could not create tool schema for action: {str(e)}")
                    continue
            
            return tool_schemas
            
        except Exception as e:
            print(f"Warning: Could not fetch user available actions, falling back to all actions: {str(e)}")
            return self._get_all_predefined_actions_openai()

    def _get_user_available_actions_langchain(self, user_id: str) -> List[BaseTool]:
        """
        Get all available actions for a specific user formatted for Langchain.
        
        Args:
            user_id: User ID to fetch available actions for
            
        Returns:
            List of Langchain BaseTool objects
            
        Raises:
            LumenError: If API request fails
        """
        try:
            available_actions = self.client._make_request(
                method="GET",
                endpoint="/actions/",
                params={"user_id": user_id, "llm_provider": "langchain"}
            )
            
            langchain_tools: List[BaseTool] = []
            
            for action in available_actions:
                if isinstance(action, dict):
                    tool = self._create_langchain_tool_from_dict(action, user_id)
                    if tool:
                        langchain_tools.append(tool)
            
            return langchain_tools
            
        except Exception as e:
            print(f"Warning: Could not fetch user available actions for Langchain, falling back to all actions: {str(e)}")
            return self._get_all_predefined_actions_langchain(user_id)

    def _get_all_predefined_actions_openai(self) -> List[ChatCompletionToolParam]:
        """
        Get all predefined actions as a fallback when user-specific actions can't be retrieved (OpenAI format).
        
        Returns:
            List of ChatCompletionToolParam objects for all predefined actions
        """
        tool_schemas: List[ChatCompletionToolParam] = []
        processed_providers = set()
        
        for action in ACTION_METADATA.keys():
            try:
                self._process_action_constant_openai(action, tool_schemas)
            except Exception as e:
                print(f"Warning: Could not process predefined action '{action}': {str(e)}")
                continue
        
        return tool_schemas

    def _get_all_predefined_actions_langchain(self, user_id: str) -> List[BaseTool]:
        """
        Get all predefined actions formatted for Langchain as a fallback.
        
        Returns:
            List of Langchain BaseTool objects
        """
        langchain_tools: List[BaseTool] = []
        
        for action in ACTION_METADATA.keys():
            try:
                metadata = self.get_action_metadata(action)
                schema = self._get_tool_schema_langchain(
                    action_name=metadata["friendly_name"],
                    provider=metadata["provider"],
                    service=metadata["service"]
                )
                tool = self._create_langchain_tool_from_dict(schema, user_id)
                if tool:
                    langchain_tools.append(tool)
            except Exception as e:
                print(f"Warning: Could not process predefined action '{action}' for Langchain: {str(e)}")
                continue
        
        return langchain_tools

    def get_functions(
        self,
        user_id: str,
        tools: Optional[List[str]] = None,
        connection_id: Optional[str] = None
    ) -> Dict[str, ToolFunction]:
        """
        Get multiple ToolFunction objects for direct execution.
        
        Args:
            user_id: User ID for function execution
            tools: List of action constants or app constants, or None for all tools
            connection_id: Optional connection ID for the functions
            
        Returns:
            Dictionary mapping action constants to ToolFunction objects
            
        Raises:
            ValueError: If parameters are invalid
            LumenError: If function creation fails
        """
        from lumen_tools.constants import APP_TO_ACTIONS
        
        self._validate_user_id(user_id)
        validated_tools = self._validate_and_prepare_tools(tools)
        
        functions = {}
        processed_providers = set()
        
        for tool in validated_tools:
            if tool in APP_TO_ACTIONS:
                self._create_functions_from_app(
                    tool, functions, user_id, connection_id, processed_providers
                )
            else:
                self._create_function_from_action(
                    tool, functions, user_id, connection_id
                )
        
        return functions
    
    def find_actions_by_use_case(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Find actions by use case using semantic search.
        
        Args:
            user_id: User ID for filtering available actions
            query: Natural language query describing the use case (e.g., "Send an email")
            
        Returns:
            List of action dictionaries matching the use case
            
        Raises:
            ValueError: If user_id or query is empty
            LumenError: If search request fails
            
        Example:
            actions = tools_manager.find_actions_by_use_case(
                user_id="687e16abd069986909a0a5f9",
                query="Send an email"
            )
        """
        self._validate_user_id(user_id)
        self._validate_query(query)
        
        params = {
            "query": query.strip(),
            "user_id": user_id.strip()
        }
        
        return self.client._make_request(
            method="GET",
            endpoint="/embeddings/search",
            params=params
        )
    
    def _validate_query(self, query: str) -> None:
        """Validate query parameter."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

    def _validate_user_id(self, user_id: str) -> None:
        """Validate user ID parameter."""
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")

    def _validate_and_prepare_tools(self, tools: Optional[List[str]]) -> List[str]:
        """Validate and prepare tools list."""
        if tools is None:
            return list(ACTION_METADATA.keys())
        
        if not isinstance(tools, list):
            raise ValueError("Tools must be a list or None")
        
        if not tools:
            raise ValueError("Tools list cannot be empty")
            
        return tools

    def _process_app_constant_openai(
        self, 
        app_tool: str,
        user_id: str, 
        tool_schemas: List[ChatCompletionToolParam],
        processed_providers: set
    ) -> None:
        """Process an app constant and add its tool schemas (OpenAI format)."""
        try:
            actions_response = self._get_actions_for_app_openai(app_tool, user_id)
            
            for action_name, action_data in actions_response.items():
                schema = {"type": "function", "function": action_data}
                tool_schemas.append(ChatCompletionToolParam(**schema))
                    
        except Exception as e:
            print(f"Warning: Could not process app constant '{app_tool}': {str(e)}")

    def _process_app_constant_langchain(
        self, 
        app_tool: str,
        user_id: str, 
        langchain_tools: List[BaseTool],
        processed_providers: set
    ) -> None:
        """Process an app constant and add its Langchain tool schemas."""
        try:
            actions_response = self._get_actions_for_app_langchain(app_tool, user_id)
            
            for action_data in actions_response:
                if isinstance(action_data, dict):
                    tool = self._create_langchain_tool_from_dict(action_data, user_id)
                    if tool:
                        langchain_tools.append(tool)
                        
        except Exception as e:
            print(f"Warning: Could not process app constant '{app_tool}' for Langchain: {str(e)}")

    def _create_functions_from_app(
        self,
        app_tool: str,
        functions: Dict[str, ToolFunction],
        user_id: str,
        connection_id: Optional[str],
        processed_providers: set
    ) -> None:
        """Create ToolFunction objects from an app constant."""
        try:
            actions_response = self._get_actions_for_app_openai(app_tool, user_id)
            
            for action_name, action_schema in actions_response.items():
                action_constant = self._find_action_constant_by_name(action_name)
                
                if action_constant:
                    tool_function = ToolFunction(
                        client=self.client,
                        user_id=user_id.strip(),
                        action=action_constant,
                        connection_id=connection_id,
                        schema=action_schema
                    )
                    functions[action_constant] = tool_function
                        
        except Exception as e:
            print(f"Warning: Could not create functions from app '{app_tool}': {str(e)}")

    def _get_actions_for_app_openai(self, app_constant: str, user_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all available actions for an app constant using the /actions/app endpoint (OpenAI format).
        
        Args:
            app_constant: App constant (e.g., "App.GMAIL", "App.DOCS")
            user_id: User ID for filtering available actions
            
        Returns:
            Dictionary containing all available actions for the app
            
        Raises:
            LumenError: If actions retrieval fails
        """
        params = {"app": app_constant, "user_id": user_id}
        
        actions_list = self.client._make_request(
            method="GET",
            endpoint="/actions/app",
            params=params
        )
        
        if isinstance(actions_list, list):
            actions_dict = {}
            for action_item in actions_list:
                if isinstance(action_item, dict):
                    func = action_item.get("function")
                    if isinstance(func, dict) and "name" in func:
                        actions_dict[func["name"]] = func
            return actions_dict
        
        return actions_list if isinstance(actions_list, dict) else {}

    def _get_actions_for_app_langchain(self, app_constant: str, user_id: str) -> List[BaseTool]:
        """
        Get all available actions for an app constant formatted for Langchain.
        
        Args:
            app_constant: App constant (e.g., "App.GMAIL", "App.DOCS")
            user_id: User ID for filtering available actions
            
        Returns:
            List of Langchain-formatted tool dictionaries
            
        Raises:
            LumenError: If actions retrieval fails
        """
        params = {"app": app_constant, "user_id": user_id, "llm_provider": "langchain"}
        
        actions_list = self.client._make_request(
            method="GET",
            endpoint="/actions/app",
            params=params
        )
        
        return actions_list if isinstance(actions_list, list) else []

    def _find_action_constant_by_name(self, action_name: str) -> Optional[str]:
        """Find action constant by matching friendly name only."""
        for action, metadata in ACTION_METADATA.items():
            if metadata["friendly_name"] == action_name:
                return action
        return None

    def _process_action_constant_openai(
        self, 
        action_tool: str, 
        tool_schemas: List[ChatCompletionToolParam]
    ) -> None:
        """Process an action constant and add its tool schema (OpenAI format)."""
        try:
            metadata = self.get_action_metadata(action_tool)

            schema = self._get_tool_schema_openai(
                action_name=metadata["friendly_name"],
                provider=metadata["provider"],
                service=metadata["service"]
            )

            if "function" not in schema:
                schema = {"type": "function", "function": schema}

            tool_schemas.append(ChatCompletionToolParam(**schema))

        except Exception as e:
            print(f"Warning: Could not process action constant '{action_tool}': {str(e)}")

    def _process_action_constant_langchain(
        self, 
        action_tool: str, 
        langchain_tools: List[BaseTool], 
        user_id: str
    ) -> None:
        """Process an action constant and add its Langchain tool schema."""
        try:
            metadata = self.get_action_metadata(action_tool)

            schema = self._get_tool_schema_langchain(
                action_name=metadata["friendly_name"],
                provider=metadata["provider"],
                service=metadata["service"]
            )

            tool = self._create_langchain_tool_from_dict(schema, user_id)
            if tool:
                langchain_tools.append(tool)

        except Exception as e:
            print(f"Warning: Could not process action constant '{action_tool}' for Langchain: {str(e)}")

    def _create_function_from_action(
        self,
        action_tool: str,
        functions: Dict[str, ToolFunction],
        user_id: str,
        connection_id: Optional[str]
    ) -> None:
        """Create a ToolFunction object from an action constant."""
        try:
            metadata = self.get_action_metadata(action_tool)
            schema = self._get_tool_schema_openai(
                action_name=metadata["friendly_name"],
                provider=metadata["provider"],
                service=metadata["service"]
            )
            
            tool_function = ToolFunction(
                client=self.client,
                user_id=user_id.strip(),
                action=action_tool,
                connection_id=connection_id,
                schema=schema
            )
            
            functions[action_tool] = tool_function
            
        except Exception as e:
            print(f"Warning: Could not create function for action '{action_tool}': {str(e)}")

    def _find_action_constant(self, action_name: str, provider: str, service: str) -> Optional[str]:
        """Find action constant by matching metadata."""
        for action, metadata in ACTION_METADATA.items():
            if (metadata["friendly_name"] == action_name and 
                metadata["provider"] == provider and 
                metadata["service"] == service):
                return action
        return None

    def _get_provider_service_from_app(self, app_constant: str) -> str:
        """
        Get provider:service key from app constant.
        
        Args:
            app_constant: App constant (e.g., App.GMAIL)
            
        Returns:
            String in format "provider:service" (e.g., "google:gmail")
            
        Raises:
            ValueError: If app constant is invalid
        """
        from lumen_tools.constants import APP_TO_ACTIONS
        
        actions = APP_TO_ACTIONS.get(app_constant, [])
        if not actions:
            raise ValueError(f"No actions found for app constant: {app_constant}")
        
        first_action = actions[0]
        metadata = ACTION_METADATA.get(first_action)
        if not metadata:
            raise ValueError(f"No metadata found for action: {first_action}")
        
        return f"{metadata['provider']}:{metadata['service']}"

    def _get_tool_schema_openai(self, action_name: str, provider: str, service: str) -> Dict[str, Any]:
        """
        Get schema for a specific action (OpenAI format).
        
        Args:
            action_name: Friendly name of the action (e.g., "send_email")
            provider: Provider name (e.g., "google")
            service: Service name (e.g., "gmail")
            
        Returns:
            Dictionary containing the action schema
            
        Raises:
            LumenError: If schema retrieval fails
        """
        params = {"provider": provider, "service": service}
        
        return self.client._make_request(
            method="GET",
            endpoint=f"/actions/{action_name}/schema",
            params=params
        )

    def _get_tool_schema_langchain(self, action_name: str, provider: str, service: str) -> Dict[str, Any]:
        """
        Get schema for a specific action formatted for Langchain.
        
        Args:
            action_name: Friendly name of the action (e.g., "send_email")
            provider: Provider name (e.g., "google")
            service: Service name (e.g., "gmail")
            
        Returns:
            Dictionary containing the Langchain-formatted action schema
            
        Raises:
            LumenError: If schema retrieval fails
        """
        params = {"provider": provider, "service": service, "llm_provider": "langchain"}
        
        return self.client._make_request(
            method="GET",
            endpoint=f"/actions/{action_name}/schema",
            params=params
        )

    def _get_available_actions(self, provider: str, service: str, user_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all available actions for a provider/service combination.
        
        Args:
            provider: Provider name (e.g., "google")
            service: Service name (e.g., "gmail")
            
        Returns:
            Dictionary containing all available actions for the provider/service
            
        Raises:
            LumenError: If actions retrieval fails
        """
        params = {"provider": provider, "service": service, "user_id": user_id}
        
        actions_list = self.client._make_request(
            method="GET",
            endpoint="/actions/",
            params=params
        )
        
        if isinstance(actions_list, list):
            actions_dict = {}
            for action_item in actions_list:
                if isinstance(action_item, dict):
                    func = action_item.get("function")
                    if isinstance(func, dict) and "name" in func:
                        actions_dict[func["name"]] = func
            return actions_dict
        
        return actions_list if isinstance(actions_list, dict) else {}
    
    def _create_langchain_tool_from_dict(self, tool_data: Dict[str, Any], user_id: str) -> Optional[BaseTool]:
        try:
            func_info = tool_data.get('function', tool_data)
            name = func_info.get('name')
            description = func_info.get('description', '')
            
            if not name:
                return None
            
            args_schema = self._get_args_schema_from_function(func_info)
            
            func = self._create_tool_function(name, user_id, args_schema)
            
            return StructuredTool.from_function(
                func=func,
                name=name,
                description=description,
                args_schema=args_schema,
                return_direct=tool_data.get('return_direct', False)
            )
            
        except Exception as e:
            print(f"Warning: Could not create Langchain tool from dict: {str(e)}")
            return None
    
    def _get_args_schema_from_function(self, func_info: Dict[str, Any]) -> Optional[type]:
        """Extract args schema from function info for Langchain compatibility."""
        try:
            from pydantic import Field, create_model
            from typing import List
            print("func_info: ", func_info)
            parameters = func_info.get('args_schema', {})
            properties = parameters.get('properties', {})
            required = parameters.get('required', [])
            
            if not properties:
                return None
            
            field_definitions = {}
            for prop_name, prop_info in properties.items():
                if prop_name == 'to' and prop_info.get('type') == 'array':
                    field_type = List[str]
                else:
                    field_type = self._get_python_type(prop_info.get('type', 'string'))
                
                field_default = ... if prop_name in required else None
                
                field_definitions[prop_name] = (
                    field_type,
                    Field(default=field_default, description=prop_info.get('description', ''))
                )
            
            return create_model(f"{func_info.get('name', 'Tool')}Args", **field_definitions)
            
        except Exception as e:
            print(f"Warning: Could not create args schema: {str(e)}")
            return None

    def _get_python_type(self, json_type: str) -> type:
        """Map JSON schema types to Python types."""
        type_map = {
            'string': str,
            'integer': int,
            'number': float,
            'boolean': bool,
            'array': list,
            'object': dict
        }
        return type_map.get(json_type, str)
        

    def _create_tool_function(self, action_name: str, user_id: str, args_schema: Optional[type]):
        """Create a function for StructuredTool execution with proper parameter validation."""
        def tool_function(**kwargs):
            """Execute the tool action."""
            try:
                if args_schema:
                    validated_args = args_schema(**kwargs)
                    kwargs = validated_args.dict()
                
                response = self.client.provider.handle_tool_calls(
                    user_id=user_id,
                    response={
                        'action': action_name,
                        'params': kwargs
                    }
                )
                
                if response.get("error"):
                    raise Exception(f"Tool execution failed: {response['error']}")
                
                return response
                
            except Exception as e:
                raise Exception(f"Tool execution error: {str(e)}")
        
        return tool_function