"""
File: /providers/langchain.py
Created Date: Tuesday September 2nd 2025
Author: Developer
-----
Last Modified: Wednesday September 3rd 2025
Modified By: Developer
-----
"""

class LangchainProvider:
    """
    Provider for integrating Lumen tools with Langchain framework.
   
    This provider converts Lumen tool metadata into Langchain-compatible tools
    that can be used with Langchain agents and chains.
    """
   
    def __init__(self, client=None):
        """
        Initialize the Langchain provider.
        
        Args:
            client: LumenClient instance for API communication
        """
        self.provider_type = "langchain"
        self.client = client
    
    def handle_tool_calls(self, user_id: str, tool_calls_data: dict) -> dict:
        """
        Handle tool calls from Langchain by delegating to ProviderManager.
        
        Args:
            user_id: User ID for execution context
            tool_calls_data: Dictionary containing tool call information
            
        Returns:
            Dictionary containing execution results
        """
        if not self.client:
            raise ValueError("Client not initialized for LangchainProvider")
        
        return self.client.provider.handle_tool_calls(user_id, tool_calls_data)
