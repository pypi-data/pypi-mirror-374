import pytest
from pytest import MonkeyPatch
import os
from pytest_mock import MockerFixture

from ...conftest import mock_handshake_response

from synthex import Synthex
from synthex.config import config


@pytest.mark.unit
def test_synthex_instantiation_apikey_in_env_success():
    """
    This test ensures that the Synthex class can be successfully instantiated without raising
    an exception when the required API key is available in the environment and not explicitly
    passed as an argument upon instantiation. If instantiation fails, the test will fail.
    """

    # Check if the API_KEY environment variable is set, otherwise skip the test.
    api_key = os.getenv("API_KEY")
    if api_key is None:
        pytest.skip("API_KEY environment variable not set. Skipping test.")

    try:
        Synthex()
    except Exception:
        pytest.fail("Synthex instantiation failed with API key in environment variable.")

@pytest.mark.unit
def test_synthex_instantiation_apikey_in_argument_success(monkeypatch: MonkeyPatch):
    """
    This test ensures that the Synthex class can be successfully instantiated without raising
    an exception when the required API key is not present in the environment variables, but is 
    passed explicitly at instantiation. If instantiation fails, the test will fail.
    Arguments:
        monkeypatch (MonkeyPatch): pytest fixture for safely modifying environment variables.
    """

    # Remove .env file, so the API KEY does not get picked up by Synthex.
    os.remove(".env")
    # Remove the API_KEY environment variable if it exists.
    if "API_KEY" in os.environ:
        monkeypatch.delenv("API_KEY", raising=False)

    # Check that the API_KEY environment variable is not set, otherwise skip the test.
    api_key = os.getenv("API_KEY")
    if api_key is not None:
        pytest.skip("API_KEY environment variable set. Skipping test.")
        
    # Remove API_KEY from the config object
    monkeypatch.setattr(config, "API_KEY", None)

    try:
        Synthex(api_key="test_api_key")
    except Exception:
        pytest.fail("Synthex instantiation failed with API key passed as an argument.")

@pytest.mark.unit
def test_synthex_instantiation_anon_id_file_creation(
    mock_handshake: MockerFixture, synthex_no_api_key: Synthex
):
    """
    This test ensures that the Synthex class creates the anonymous ID file with the correct content when
    instantiated without an API key and the anonymous ID file is not present.

    Arguments:
        mock_handshake (MockerFixture): A pytest fixture to mock the handshake response.
        synthex_no_api_key (Synthex): An instance of Synthex that is initialized without an API key.
    """

    # Remove the anonymous ID file if it exists
    os.remove(config.ANON_ID_FILE)
    
    # Skip the test if the anon id file exists
    assert not os.path.exists(config.ANON_ID_FILE)

    # Create the Synthex instance without an API key
    Synthex()

    # Check if the anonymous ID file was created
    assert os.path.exists(config.ANON_ID_FILE)
    with open(config.ANON_ID_FILE, "r") as f:
        content = f.read().strip()
    assert content == mock_handshake_response.anon_id
    
@pytest.mark.unit
def test_synthex_instantiation_anon_id_in_header(mock_handshake: MockerFixture, synthex_no_api_key: Synthex):
    """
    This test ensures that the Synthex._client is initialized with the anonymous ID in the header, if no
    API key is provided during instantiation.

    Arguments:
        mock_handshake (MockerFixture): A pytest fixture to mock the handshake response.
        synthex_no_api_key (Synthex): An instance of Synthex that is initialized without an API key.
    """
    
    # Remove the anonymous ID file if it exists
    os.remove(config.ANON_ID_FILE)

    # Ensure the anonymous ID file exists
    if os.path.exists(config.ANON_ID_FILE):
        pytest.skip("Anonymous ID file already exists. Skipping test.")

    # Create the Synthex instance without an API key
    synthex = Synthex()

    # Check that no API key is set
    if synthex._client.API_KEY is not None: # type: ignore
        pytest.skip("API key is not None. Skipping test.")
        
    assert synthex._client.session.headers[config.SYNTHEX_ANON_ID_HEADER] == mock_handshake_response.anon_id # type: ignore
    
@pytest.mark.unit
def test_synthex_instantiation_no_anon_id_header(mock_handshake: MockerFixture, synthex: Synthex):
    """
    This test ensures that the Synthex._client is not initialized with the anonymous ID in the header, if an
    API key is provided during instantiation.

    Arguments:
        mock_handshake (MockerFixture): A pytest fixture to mock the handshake response.
        synthex (Synthex): An instance of Synthex.
    """
    
    # Remove the anonymous ID file if it exists
    os.remove(config.ANON_ID_FILE)

    # Ensure the anonymous ID file exists
    if os.path.exists(config.ANON_ID_FILE):
        pytest.skip("Anonymous ID file already exists. Skipping test.")

    # Create the Synthex instance without an API key
    synthex = Synthex(api_key="test")
        
    # Check that there is no anonymous ID in the headers
    assert config.SYNTHEX_ANON_ID_HEADER not in synthex._client.session.headers # type: ignore