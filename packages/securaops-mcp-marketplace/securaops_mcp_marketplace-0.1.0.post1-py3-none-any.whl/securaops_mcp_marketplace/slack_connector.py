import requests
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    status: str
    message_id: Optional[str] = None
    error: Optional[str] = None


class SlackConnector:
    def __init__(self, api_key: str, base_url: str = "https://slack.com/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def send_message(self, channel: str, message: str) -> Dict[str, Any]:
        """
        Send a message to a Slack channel
        
        Args:
            channel: Channel name (e.g., "#general") or ID
            message: Message text to send
            
        Returns:
            Dictionary with status and message ID
        """
        payload = {
            "channel": channel,
            "text": message
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat.postMessage",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("ok"):
                return MessageResponse(
                    status="sent",
                    message_id=data.get("ts")
                ).dict()
            else:
                return MessageResponse(
                    status="error",
                    error=data.get("error", "Unknown error")
                ).dict()
                
        except requests.exceptions.RequestException as e:
            return MessageResponse(
                status="error",
                error=str(e)
            ).dict()
    
    def test_connection(self) -> bool:
        """Test if the API key is valid"""
        try:
            response = self.session.post(f"{self.base_url}/auth.test")
            return response.json().get("ok", False)
        except:
            return False