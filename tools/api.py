from typing import Dict, Any, Optional
import logging
import requests
from datetime import datetime
import json
import os

class APIManager:
    def __init__(self):
        self.logger = logging.getLogger("api_manager")
        self.base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
        self.api_key = os.environ.get("API_KEY")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request"""
        try:
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GET request failed: {e}")
            raise

    async def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make POST request"""
        try:
            response = self.session.post(
                f"{self.base_url}/{endpoint}",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"POST request failed: {e}")
            raise

    async def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make PUT request"""
        try:
            response = self.session.put(
                f"{self.base_url}/{endpoint}",
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"PUT request failed: {e}")
            raise

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        try:
            response = self.session.delete(
                f"{self.base_url}/{endpoint}"
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"DELETE request failed: {e}")
            raise

    async def upload_file(self, endpoint: str, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload file with metadata"""
        try:
            files = {
                'file': open(file_path, 'rb')
            }
            
            data = {}
            if metadata:
                data['metadata'] = json.dumps(metadata)
            
            response = self.session.post(
                f"{self.base_url}/{endpoint}",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"File upload failed: {e}")
            raise
        finally:
            files['file'].close()

    async def download_file(self, endpoint: str, save_path: str) -> bool:
        """Download file"""
        try:
            response = self.session.get(
                f"{self.base_url}/{endpoint}",
                stream=True
            )
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"File download failed: {e}")
            raise

    async def get_api_status(self) -> Dict[str, Any]:
        """Get API status and metrics"""
        try:
            response = await self.get("status")
            return {
                "status": "healthy" if response.get("status") == "ok" else "unhealthy",
                "latency": response.get("latency", 0),
                "uptime": response.get("uptime", 0),
                "last_checked": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get API status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_checked": datetime.now().isoformat()
            }

    def set_auth_token(self, token: str):
        """Set authentication token"""
        self.session.headers.update({
            "Authorization": f"Bearer {token}"
        })

    def clear_auth_token(self):
        """Clear authentication token"""
        self.session.headers.pop("Authorization", None)

