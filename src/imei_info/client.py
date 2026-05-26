import httpx
from typing import Optional, Any
from .models import ImeiCheckResponse
from .exceptions import raise_for_status_code, ImeiNetworkError

DEFAULT_BASE_URL = "https://api.imei.info/v5"

class ImeiClient:
    """
    Synchronous HTTP Client for the IMEI.info API v5.
    
    Suitable for scripts, cron jobs, and standard synchronous web applications.
    """
    def __init__(
        self, 
        token: str, 
        base_url: str = DEFAULT_BASE_URL, 
        timeout: float = 10.0,
        **kwargs: Any
    ):
        """
        Initialize the synchronous IMEI.info client.
        
        :param token: Your Bearer Token from dash.imei.info
        :param base_url: API Gateway URL (defaults to production v5)
        :param timeout: Connection and request timeout in seconds
        """
        self.token = token
        self.base_url = base_url.rstrip("/")
        
        # Initialize client with authorization headers
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=timeout,
            **kwargs
        )

    def check_imei(self, imei: str, service_id: int = 0, sync: bool = False) -> ImeiCheckResponse:
        """
        Check and retrieve full specifications and status of a device using its 15-digit IMEI.
        
        :param imei: 15-digit IMEI number
        :param service_id: Service ID to use for the check. Default is 0.
        :param sync: True to use instant /api-sync/ endpoint, False for /api/ queue endpoint.
        :return: ImeiCheckResponse object containing report details
        :raises ImeiAuthenticationError: If the token is invalid (401)
        :raises ImeiInsufficientCreditsError: If balance is low (402)
        :raises ImeiValidationError: If Luhn validation fails (422)
        :raises ImeiRateLimitError: If API rate limits are hit (429)
        :raises ImeiServerError: If IMEI.info server is down (500)
        :raises ImeiNetworkError: For connection/timeout errors
        """
        try:
            # Determine endpoint path based on gateway destination (Production dash.imei.info vs Local Prototype Mock)
            if "dash.imei.info" in self.base_url:
                path_prefix = "/api-sync/check" if sync else "/api/check"
                endpoint = f"{self.base_url}{path_prefix}/{service_id}/"
                params = {"API_KEY": self.token, "format": "json", "imei": imei}
            else:
                path_prefix = "/api-sync/imei/check" if sync else "/api/imei/check"
                endpoint = f"{self.base_url}{path_prefix}"
                params = {"API_KEY": self.token, "format": "json", "imei": imei, "service_id": service_id}

            response = self.client.get(endpoint, params=params)
            # Raise exception if status is not 200
            raise_for_status_code(response.status_code, response.text)
            
            # Parse successful JSON response
            return ImeiCheckResponse.from_dict(response.json())
        except httpx.RequestError as exc:
            raise ImeiNetworkError(str(exc), exc) from exc

    def get_search_result(self, history_id: int) -> ImeiCheckResponse:
        """
        Retrieve the status and technical details report of a queued IMEI search history item.
        
        :param history_id: The search history ID returned in the 202 response
        :return: ImeiCheckResponse containing report details and status
        """
        try:
            endpoint = f"{self.base_url}/api/search_history/{history_id}/"
            params = {"API_KEY": self.token, "format": "json"}
            response = self.client.get(endpoint, params=params)
            raise_for_status_code(response.status_code, response.text)
            return ImeiCheckResponse.from_dict(response.json())
        except httpx.RequestError as exc:
            raise ImeiNetworkError(str(exc), exc) from exc

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self.client.close()

    def __enter__(self) -> "ImeiClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()


class AsyncImeiClient:
    """
    Asynchronous HTTP Client for the IMEI.info API v5.
    
    Highly efficient client for asynchronous web frameworks (FastAPI, Tornado)
    and high-performance async scripts.
    """
    def __init__(
        self, 
        token: str, 
        base_url: str = DEFAULT_BASE_URL, 
        timeout: float = 10.0,
        **kwargs: Any
    ):
        """
        Initialize the asynchronous IMEI.info client.
        
        :param token: Your Bearer Token from dash.imei.info
        :param base_url: API Gateway URL (defaults to production v5)
        :param timeout: Connection and request timeout in seconds
        """
        self.token = token
        self.base_url = base_url.rstrip("/")
        
        # Initialize client with authorization headers
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=timeout,
            **kwargs
        )

    async def check_imei(self, imei: str, service_id: int = 0, sync: bool = False) -> ImeiCheckResponse:
        """
        Asynchronously check and retrieve full specifications and status of a device.
        
        :param imei: 15-digit IMEI number
        :param service_id: Service ID to use for the check. Default is 0.
        :param sync: True to use instant /api-sync/ endpoint, False for /api/ queue endpoint.
        :return: ImeiCheckResponse object containing report details
        :raises ImeiAuthenticationError: If the token is invalid (401)
        :raises ImeiInsufficientCreditsError: If balance is low (402)
        :raises ImeiValidationError: If Luhn validation fails (422)
        :raises ImeiRateLimitError: If API rate limits are hit (429)
        :raises ImeiServerError: If IMEI.info server is down (500)
        :raises ImeiNetworkError: For connection/timeout errors
        """
        try:
            # Determine endpoint path based on gateway destination (Production dash.imei.info vs Local Prototype Mock)
            if "dash.imei.info" in self.base_url:
                path_prefix = "/api-sync/check" if sync else "/api/check"
                endpoint = f"{self.base_url}{path_prefix}/{service_id}/"
                params = {"API_KEY": self.token, "format": "json", "imei": imei}
            else:
                path_prefix = "/api-sync/imei/check" if sync else "/api/imei/check"
                endpoint = f"{self.base_url}{path_prefix}"
                params = {"API_KEY": self.token, "format": "json", "imei": imei, "service_id": service_id}

            response = await self.client.get(endpoint, params=params)
            # Raise exception if status is not 200
            raise_for_status_code(response.status_code, response.text)
            
            # Parse successful JSON response
            return ImeiCheckResponse.from_dict(response.json())
        except httpx.RequestError as exc:
            raise ImeiNetworkError(str(exc), exc) from exc

    async def get_search_result(self, history_id: int) -> ImeiCheckResponse:
        """
        Asynchronously retrieve the status and technical details of a queued history item.
        
        :param history_id: The search history ID returned in the 202 response
        :return: ImeiCheckResponse containing report details and status
        """
        try:
            endpoint = f"{self.base_url}/api/search_history/{history_id}/"
            params = {"API_KEY": self.token, "format": "json"}
            response = await self.client.get(endpoint, params=params)
            raise_for_status_code(response.status_code, response.text)
            return ImeiCheckResponse.from_dict(response.json())
        except httpx.RequestError as exc:
            raise ImeiNetworkError(str(exc), exc) from exc

    async def close(self) -> None:
        """Asynchronously close the underlying HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "AsyncImeiClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
