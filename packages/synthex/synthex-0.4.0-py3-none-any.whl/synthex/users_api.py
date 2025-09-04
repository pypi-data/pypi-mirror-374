from .api_client import APIClient

from .endpoints import GET_CURRENT_USER_ENDPOINT
from .models import UserResponseModel
from .exceptions import ServerError


class UsersAPI:
    """
    UsersAPI provides methods for managing user-related operations.
    """
    
    def __init__(self, client: APIClient):
        self._client: APIClient = client
        
    def me(self) -> UserResponseModel:
        """
        Retrieves the current user's information from the API.

        Returns:
            UserResponseModel: A model containing the current user's information.
        """
        
        response = self._client.get(GET_CURRENT_USER_ENDPOINT)
        if not response or not response.data:
            raise ServerError("Failed to retrieve user information.")
                
        return UserResponseModel.model_validate(response.data)