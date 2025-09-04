import httpx
from typing import Optional, Any

from .endpoints import API_BASE_URL, PING_ENDPOINT
from .models import SuccessResponse
from .exceptions import *
from .config import config


class APIClient:
    """
    A utility class for interacting with a RESTful API. It provides methods for sending HTTP 
    requests to specified endpoints, handling errors, and managing authentication headers.
    """
    
    BASE_URL = API_BASE_URL
    
    def __init__(self, api_key: Optional[str] = None, anon_id: Optional[str] = None):
        self.API_KEY = api_key
        self.session = httpx.Client(
            base_url=self.BASE_URL,
            headers={ "Accept": "application/json", "User-Agent": "synthex" },
            timeout=30.0
        )
        if self.API_KEY:
            self.session.headers.update({ "X-API-Key": f"{self.API_KEY}" })
        # The Anon ID header is only needed if no API key is provided.
        if not self.API_KEY and anon_id:
            self.session.headers.update({ config.SYNTHEX_ANON_ID_HEADER: f"{anon_id}" })
        
    def _handle_errors(self, response: httpx.Response) -> None:
        """
        Handles HTTP response errors by raising appropriate exceptions based on the status code.
        Args:
            response (httpx.Response): The HTTP response object to evaluate.
        Raises:
            AuthenticationError: If the response status code is 401 (Unauthorized).
            NotFoundError: If the response status code is 404 (Not Found).
            RateLimitError: If the response status code is 429 (Rate Limit Exceeded).
            ServerError: If the response status code is in the range 500-599 (Server Error).
        """
        try:
            error_details = response.json()
        except Exception:
            error_details = response.text

        status = response.status_code

        if status == 400:
            raise BadRequestError("Bad request.", status, str(response.url), error_details)
        elif status == 401:
            raise AuthenticationError("Unauthorized.", status, str(response.url), error_details)
        elif status == 402:
            raise PaymentRequiredError("Payment required.", status, str(response.url), error_details)
        elif status == 404:
            raise NotFoundError("Not found.", status, str(response.url), error_details)
        elif status == 422:
            raise ValidationError("Validation error.", status, str(response.url), error_details)
        elif status == 429:
            raise RateLimitError("Rate limit exceeded.", status, str(response.url), error_details)
        elif 500 <= status < 600:
            raise ServerError("Server error.", status, str(response.url), error_details)

    def get(
        self, endpoint: str, params: Optional[dict[str, Any]] = None
    ) -> SuccessResponse[Any]:
        """
        Sends a GET request to the specified API endpoint.
        Args:
            endpoint (str): The API endpoint to send the GET request to.
            params (Optional[dict[str, Any]]): Optional query parameters to include in the request.
        Returns:
            SuccessResponse[Any]: A response object containing the parsed JSON data.
        Raises:
            SynthexError: If the response contains an HTTP error status code.
        """

        response = self.session.get(endpoint, params=params)
        self._handle_errors(response)
        return SuccessResponse(**response.json())

    def post(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> SuccessResponse[Any]:
        """
        Sends a POST request to the specified endpoint with the provided data.
        Args:
            endpoint (str): The API endpoint to send the POST request to.
            data (Optional[dict[str, Any]]): The JSON-serializable data to include in the request body. Defaults to None.
        Returns:
            SuccessResponse[Any]: The JSON response from the server.
        Raises:
            SynthexError: If the response contains an HTTP error status code.
        """

        response = self.session.post(endpoint, json=data)
        self._handle_errors(response)
        return SuccessResponse(**response.json())

    def put(
        self, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> SuccessResponse[Any]:
        """
        Sends a PUT request to the specified endpoint with the provided data.
        Args:
            endpoint (str): The API endpoint to send the PUT request to.
            data (Optional[dict[str, Any]]): The JSON-serializable dictionary to include in the request body. Defaults to None.
        Returns:
            SuccessResponse[Any]: The JSON response from the server.
        Raises:
            SynthexError: If the response contains an HTTP error status code.
        """
        
        response = self.session.put(endpoint, json=data)
        self._handle_errors(response)
        return SuccessResponse(**response.json())

    def delete(self, endpoint: str) -> SuccessResponse[Any]:
        """
        Sends a DELETE request to the specified endpoint and handles the response.
        Args:
            endpoint (str): The API endpoint to send the DELETE request to.
        Returns:
            SuccessResponse[Any]: The JSON response from the server.
        Raises:
            SynthexError: If the response contains an HTTP error status code.
        """
        
        response = self.session.delete(endpoint)
        self._handle_errors(response)
        return SuccessResponse(**response.json())
    
    def ping(self) -> bool:
        """
        Sends a ping request to the server to check connectivity.
        Returns:
            bool: True if the ping request is successful, False otherwise.
        """
        
        try:
            self.get(PING_ENDPOINT)
            return True
        except Exception:
            return False