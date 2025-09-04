from typing import Optional

from .api_client import APIClient
from .jobs_api import JobsAPI
from .users_api import UsersAPI
from .credits_api import CreditsAPI
from .decorators import auto_validate_methods
from .config import config
from .models import HandshakeResponseModel
from .endpoints import HANDSHAKE_ENDPOINT


@auto_validate_methods
class Synthex:
    """
    Synthex is a client library for interacting with the Synthex API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self._anon_id = None
        if not api_key:
            api_key=config.API_KEY
        self._client = APIClient(api_key=api_key)

        # A anon id is only needed if no API key is provided.
        if not api_key:
            self._anon_id = self._get_anon_id()
            # If no anonymous ID is found, perform a handshake to obtain one, then save it to a file.
            if not self._anon_id:
                handshake_response = self._handshake()
                self._anon_id = handshake_response.anon_id
                self._save_anon_id(self._anon_id)
            # Update the API client with the anon ID.
            self._client = APIClient(api_key=api_key, anon_id=self._anon_id)

        self.jobs = JobsAPI(self._client)
        self.users = UsersAPI(self._client)
        self.credits = CreditsAPI(self._client)

    def _get_anon_id(self) -> Optional[str]:
        """
        Retrieves the anonymous ID, if it exists.
        Returns:
            Optional[str]: The anonymous ID, if it is found; otherwise, None.
        """

        return config.ANON_ID_FILE.read_text().strip() if config.ANON_ID_FILE.is_file() \
            and config.ANON_ID_FILE.read_text().strip() else None
    
    def _save_anon_id(self, anon_id: str) -> None:
        """
        Saves the anonymous ID to a file.
        Args:
            anon_id (str): The anonymous ID to save.
        """
        
        config.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config.ANON_ID_FILE.write_text(anon_id)

    def _handshake(self) -> HandshakeResponseModel:
        response = self._client.get(HANDSHAKE_ENDPOINT)

        return HandshakeResponseModel.model_validate(response.data)

    def ping(self) -> bool:
        """
        Pings the Synthex API to check if it is reachable.
        Returns:
            bool: True if the API is reachable, False otherwise.
        """
        
        return self._client.ping()