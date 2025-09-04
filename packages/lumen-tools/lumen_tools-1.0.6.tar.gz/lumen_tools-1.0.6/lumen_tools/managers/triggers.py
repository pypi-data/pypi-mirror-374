"""
File: /managers/triggers.py
Created Date: Tuesday July 29th 2025
Author: Harsh Kumar <fyo9329@gmail.com>
-----
Last Modified: Tuesday August 12th 2025
Modified By: the developer formerly known as Harsh Kumar at <fyo9329@gmail.com>
-----
"""

from typing import Any, Dict, List, Optional

from lumen_tools.constants import EventType, ServiceType

class TriggersManager:
    """
    Manager for webhook/trigger operations.
    
    This manager handles the setup and configuration of webhooks for various
    Google services and GitHub, providing a clean interface for real-time event notifications.
    """
    
    def __init__(self, client):
        """
        Initialize triggers manager.
        
        Args:
            client: LumenClient instance for API communication
        """
        self.client = client
    
    def setup(
        self,
        user_id: str,
        service: ServiceType,
        base_url: str,
        # Gmail
        label_ids: Optional[List[str]] = None,
        google_project_id: Optional[str] = None,
        topic_name: Optional[str] = None,
        # Drive/Docs
        drive_id: Optional[str] = None,
        include_removed: Optional[bool] = True,
        # Calendar
        calendar_id: Optional[str] = "primary",
        event_types: Optional[List[EventType]] = None,
        # GitHub
        team_id: Optional[str] = None,
        owner: Optional[str] = None,
        github_events: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Set up webhook for Google services and GitHub with service-specific configuration.

        Args:
            user_id: The unique identifier for the user
            service: The Google service (GMAIL, DRIVE, CALENDAR, DOCS) or GITHUB
            base_url: URL to receive notifications
            label_ids: Label IDs for Gmail (default: ["INBOX"])
            google_project_id: Google Cloud project ID for Gmail Pub/Sub
            topic_name: Pub/Sub topic name for Gmail
            drive_id: Drive ID for Drive/Docs services
            include_removed: Include removed items for Drive/Docs (default: True)
            calendar_id: Calendar ID for Calendar service (default: "primary")
            event_types: Event types to filter for Calendar service
            team_id: GitHub team ID for GitHub service
            owner: GitHub repository owner for GitHub service
            github_events: GitHub events to listen for (default: ["push", "pull_request"])

        Returns:
            Dictionary containing webhook setup result

        Raises:
            ValueError: If required parameters are missing or invalid
            LumenError: If webhook setup fails
        """
        self._validate_setup_parameters(user_id, service, base_url)

        if service == ServiceType.GMAIL:
            if not google_project_id or not topic_name:
                raise ValueError(
                    "For Gmail service, both 'google_project_id' and 'topic_name' must be provided."
                )
        
        if service == ServiceType.GITHUB:
            if not team_id or not owner:
                raise ValueError(
                    "For GitHub service, both 'team_id' and 'owner' must be provided."
                )

        payload = {
            "webhook_url": base_url.strip(),
            "user_id": user_id.strip()
        }

        self._add_service_specific_config(payload, service, {
            'label_ids': label_ids,
            'google_project_id': google_project_id,
            'topic_name': topic_name,
            'drive_id': drive_id,
            'include_removed': include_removed,
            'calendar_id': calendar_id,
            'event_types': event_types,
            'team_id': team_id,
            'owner': owner,
            'github_events': github_events
        })

        return self.client._make_request(
            method="POST",
            endpoint="/webhooks/setup",
            json_data=payload,
            params={"service": service.value}
        )

    def _validate_setup_parameters(self, user_id: str, service: ServiceType, base_url: str) -> None:
        """
        Validate required setup parameters.
        
        Args:
            user_id: User ID to validate
            service: Service type to validate
            base_url: Webhook URL to validate
            
        Raises:
            ValueError: If any parameter is invalid
        """
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        if not base_url or not base_url.strip():
            raise ValueError("Webhook URL cannot be empty")
        
        if not isinstance(service, ServiceType):
            raise ValueError(f"Service must be a ServiceType enum, got {type(service)}")

    def _add_service_specific_config(
        self, 
        payload: Dict[str, Any], 
        service: ServiceType, 
        config: Dict[str, Any]
    ) -> None:
        """
        Add service-specific configuration to the payload.
        
        Args:
            payload: Base payload dictionary to modify
            service: Service type for configuration
            config: Configuration parameters dictionary
        """
        if service == ServiceType.GMAIL:
            payload["label_ids"] = config.get('label_ids') or ["INBOX"]
            
            google_project_id = config.get("google_project_id")
            topic_name = config.get("topic_name")

            if not google_project_id or not topic_name:
                raise ValueError(
                    "For Gmail service, both 'google_project_id' and 'topic_name' must be provided."
                )
            
            payload["google_project_id"] = google_project_id
            payload["topic_name"] = topic_name
                        
        elif service in (ServiceType.DRIVE, ServiceType.DOCS):
            if config.get('drive_id'):
                payload["drive_id"] = config['drive_id']
            payload["include_removed"] = config.get('include_removed', True)
            
        elif service == ServiceType.CALENDAR:
            payload["calendar_id"] = config.get('calendar_id', "primary")
            if config.get('event_types'):
                payload["event_types"] = [event.value for event in config['event_types']]
        
        elif service == ServiceType.GITHUB:
            team_id = config.get('team_id')
            owner = config.get('owner')
            
            if not team_id or not owner:
                raise ValueError(
                    "For GitHub service, both 'team_id' and 'owner' must be provided."
                )
            
            payload["team_id"] = team_id
            payload["owner"] = owner
            payload["events"] = config.get('github_events') or ["push", "pull_request"]