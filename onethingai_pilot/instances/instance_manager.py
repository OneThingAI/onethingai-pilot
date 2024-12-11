import logging
import requests
from typing import Dict, Optional, List
import time
from .models import (
    ResourceQuery,
    ConsumeQuery,
    InstanceConfigQuery,
    InstanceQuery,  
    PrivateImageResponse,
    ResourceResponse,
    InstanceCreateResponse,
    InstanceResponse,
    WalletDetailResponse,
    WalletConsumeResponse,
    APIResponse,
    PrivateImageItem,
)

class OneThingAIInstance:
    """Manages OneThingAI instance lifecycle."""
    
    def __init__(self, 
                 api_key: str, 
                 base_url: str = "https://api-lab.onethingai.com",
                 max_retries: int = 3,
                 timeout: int = 10,
                 retry_delay: float = 1.0):
        self.api_key = api_key
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        self.logger = logging.getLogger("OneThingAIInstance")

    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     args: Optional[Dict] = None,
                     timeout: Optional[int] = None,
                     max_retries: Optional[int] = None) -> Dict:
        """Make HTTP request to OneThingAI API with retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request payload
            timeout: Request timeout in seconds (overrides instance default)
            max_retries: Maximum retry attempts (overrides instance default)
        """
        url = f"{self.base_url}/{endpoint}"
        timeout = timeout or self.timeout
        retries = max_retries or self.max_retries
        attempt = 0
        
        while attempt < retries:
            try:
                if method == "GET":
                    response = requests.request(
                        method, 
                        url, 
                        headers=self.headers, 
                        params=args.dict() if args else None, 
                        timeout=timeout
                    )
                else:
                    response = requests.request(
                        method, 
                        url, 
                        headers=self.headers, 
                        json=args.dict() if args else None, 
                        timeout=timeout
                    )
                response.raise_for_status()
                return APIResponse(**response.json())
                
            except requests.exceptions.Timeout:
                attempt += 1
                if attempt == retries:
                    self.logger.error(f"Request timed out after {retries} attempts")
                    raise
                self.logger.warning(f"Request timed out, retrying ({attempt}/{retries})")
                time.sleep(self.retry_delay * attempt)  # Exponential backoff
                
            except requests.exceptions.RequestException as e:
                if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code >= 500:
                    # Retry on 5xx errors
                    attempt += 1
                    if attempt == retries:
                        self.logger.error(f"API request failed after {retries} attempts: {str(e)}")
                        raise
                    self.logger.warning(f"Server error, retrying ({attempt}/{retries})")
                    time.sleep(self.retry_delay * attempt)
                else:
                    # Don't retry on 4xx errors or other exceptions
                    self.logger.error(f"API request failed: {str(e)}")
                    raise

    def get_private_image_list(self) -> PrivateImageResponse:
        """Get list of available images."""
        try:
            response = self._make_request("GET", "api/v1/app/private/image/list")
            if response.code == 0:
                # Create PrivateImageResponse with data
                return PrivateImageResponse(data=response.data)
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to get private image list: {str(e)}")

    def get_public_image_list(self) -> None:
        """Get list of available images."""
        # TODO: Implement this
        pass 

    def get_available_resources(self, query: ResourceQuery) -> ResourceResponse:
        """Get available resources."""
        try:
            response = self._make_request("GET", "api/v1/resources", query)
            if response.code == 0:
                return ResourceResponse(**response.data)
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to get available resources: {str(e)}")


    def get_instance_list(self, query: InstanceQuery) -> InstanceResponse:
        """Get list of instances."""
        try:
            response = self._make_request("GET", "api/v1/app", query)
            if response.code == 0:
                return InstanceResponse(**response.data)
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to get instance list: {str(e)}")

    def create(self, instance_config: InstanceConfigQuery) -> InstanceCreateResponse:
        """Create a new instance with specified configuration."""
        try:
            response = self._make_request("POST", "api/v2/app", instance_config)
            if response.code == 0:
                return InstanceCreateResponse(**response.data)
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to create instance: {str(e)}")

    def stop(self, app_id: str) -> Dict:
        """Stop a running instance."""
        try:
            response = self._make_request("PUT", f"api/v1/app/operate/shutdown/{app_id}")
            if response.code == 0:
                return response
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to stop instance: {str(e)}")

    def delete(self, app_id: str) -> Dict:
        """Delete an instance."""
        try:
            response = self._make_request("DELETE", f"api/v1/app/{app_id}")
            if response.code == 0:
                return response
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to delete instance: {str(e)}")

    def start(self, app_id: str) -> Dict:
        """Start a stopped instance."""
        try:
            response = self._make_request("PUT", f"api/v1/app/operate/boot/{app_id}")
            if response.code == 0:
                return response
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to start instance: {str(e)}")

    def get_wallet_detail(self) -> WalletDetailResponse:
        """Get user's wallet/account balance details."""
        try:
            response = self._make_request("GET", "api/v1/account/wallet/detail")
            if response.code == 0:
                return WalletDetailResponse(**response.data)
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to get wallet details: {str(e)}")


    def get_wallet_consume(self, query: ConsumeQuery) -> WalletConsumeResponse:
        """Get user's consumption/billing records.
        
        Args:
            query: ConsumeQuery object containing:
                page: Page number (required)
                page_size: Items per page, must be between 1-100 (required)
                app_id: Optional instance ID to filter by
                business_type: Optional transaction type filter:
                    1=Instance usage
                    2=Image storage
                    3=File storage
                    4=Instance expansion
        
        Returns:
            WalletConsumeResponse object containing list of consumption records
            
        Raises:
            Exception: If API request fails
        """
        try:
            response = self._make_request(
                "GET", 
                "api/v1/account/wallet/consume/query",
                params=query.dict()
            )
            if response.code == 0:
                return WalletConsumeResponse(**response.data)
            else:
                raise Exception(response.msg)
        except Exception as e:
            raise Exception(f"Failed to get consumption records: {str(e)}")

    def get_metrics(self, 
                    instance_id: str, 
                    timeout: Optional[int] = None,
                    max_retries: Optional[int] = None) -> None:
        """Get instance metrics."""
        # TODO: Implement this
        pass