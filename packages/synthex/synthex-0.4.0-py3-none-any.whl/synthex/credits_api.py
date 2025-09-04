from .api_client import APIClient

from .endpoints import GET_CREDITS_ENDPOINT
from .models import CreditResponseModel


class CreditsAPI:
    """
    CreditsAPI provides methods for managing credits.
    """
    
    def __init__(self, client: APIClient):
        self._client: APIClient = client

    def __call__(self) -> CreditResponseModel:
        """
        Retrieve credits information.
        Returns:
            CreditResponseModel: An instance of `CreditResponseModel` containing the credits data.
        """
        
        response = self._client.get(f"{GET_CREDITS_ENDPOINT}/")
        return CreditResponseModel.model_validate(response.data)