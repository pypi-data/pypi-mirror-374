import pytest
from pytest import MonkeyPatch
import os
from typing import Any
import shutil
from pathlib import Path
from typing import Generator
from pytest_mock import MockerFixture

from synthex import Synthex
from synthex.config import config
from synthex.models import HandshakeResponseModel


def fetch_synthex() -> Synthex:
    """
    Creates and returns an instance of the Synthex class using the API key 
    from the environment variables.
    Returns:
        Synthex: An instance of the Synthex class initialized with the API key.
    """
    
    api_key = config.API_KEY
    if not api_key:
        pytest.fail("API_KEY not found in environment variables")
    return Synthex(api_key)

@pytest.fixture(scope="session")
def synthex() -> Synthex:
    """
    Creates and returns an instance of the Synthex class using the API key 
    from the environment variables.
    Returns:
        Synthex: An instance of the Synthex class initialized with the API key.
    """
    
    return fetch_synthex()

@pytest.fixture(scope="function")
def short_lived_synthex() -> Synthex:
    """
    A short-lived version of the synthex fixture which is only valid for the duration of a test function.
    Returns:
        Synthex: An instance of the Synthex class initialized with the API key.
    """
    
    return fetch_synthex()

@pytest.fixture(scope="function")
def synthex_no_api_key(monkeypatch: MonkeyPatch) -> Synthex:
    """
    Creates and returns an instance of the Synthex class without an API key.
    This is used to test the behavior when no API key is provided.
    Returns:
        Synthex: An instance of the Synthex class without an API key.
    """
    
    monkeypatch.setattr(config, "API_KEY", None)

    return Synthex()

@pytest.fixture(scope="function")
def synthex_no_api_key_no_anon_id(monkeypatch: MonkeyPatch) -> Synthex:
    """
    Creates and returns an instance of the Synthex class without an API key and without an anonymous ID.
    This is used to test the behavior when no API key or anonymous id is provided.
    Returns:
        Synthex: An instance of the Synthex class without an API key.
    """
        
    monkeypatch.setattr(config, "API_KEY", None)
    synthex = Synthex()
    synthex._client.session.headers.pop(config.SYNTHEX_ANON_ID_HEADER, None) # type: ignore

    return synthex

@pytest.fixture(scope="session")
def generate_data_params() -> dict[Any, Any]:
    """
    Fixture to provide parameters for the generate_data method.
    Returns:
        dict: A dictionary containing the required data.
    """
    
    return {
        "schema_definition": {
            "question": {"type": "string"},
            "option-a": {"type": "string"},
            "option-b": {"type": "string"},
            "option-c": {"type": "string"},
            "option-d": {"type": "string"},
            "answer": {"type": "string"}
        },
        "examples": [
            {
                "question": "A gas occupies 6.0 L at 300 K and 1 atm. What is its volume at 600 K and 0.5 atm, assuming ideal gas behavior?",
                "option-a": "12.0 L",
                "option-b": "24.0 L",
                "option-c": "6.0 L",
                "option-d": "3.0 L",
                "answer": "option-b"
            }
        ],
        "requirements": [
            "Question Type: Multiple-choice questions (MCQs)",
            "Difficulty Level: High difficulty, comparable to SAT or AIEEE (JEE Main)",
            "Topic Coverage: Wide range of chemistry topics (physical, organic, inorganic)",
            "Number of Options: Each question must have four answer options",
            "Correct Answer: One of the four options must be correct and clearly marked",
            "Calculation-Based: Include mathematical/calculation-based questions",
            "Indirect Approach: Questions should be indirect and require knowledge application",
            "Conceptual Focus: Emphasize conceptual understanding, problem-solving, and analytical thinking"
        ],
        "number_of_samples": 20,
        "output_type": "csv",
        "output_path": f"test_data/output.csv"
    }
    
@pytest.fixture
def temp_env_file(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    """
    Creates a temporary .env file with predefined environment variables for testing purposes.

    Args:
        tmp_path (Path): A pytest fixture providing a temporary directory unique to the test invocation.
        monkeypatch (MonkeyPatch): A pytest fixture for safely patching and restoring environment variables and directories.
    
    Returns:
        Path: The path to the created temporary .env file.
    """
    
    env_path = tmp_path / ".env"
    env_path.write_text("API_KEY=patched_key\nFAKE_ENV=123\n")

    # Temporarily patch the env_file path
    monkeypatch.setenv("PYDANTIC_SETTINGS_PATH", str(env_path))
    monkeypatch.chdir(tmp_path)  # make it the current dir

    return env_path

mock_handshake_response = HandshakeResponseModel(anon_id="abc123")

@pytest.fixture
def mock_handshake(mocker: MockerFixture) -> MockerFixture:
    """
    Mocks the `_handshake` method of the `Synthex` class.
    Args:
        mocker (MockerFixture): The pytest-mock fixture used to patch objects.
    Returns:
        MockerFixture: The mock object for the 'generate_data' method.
    """
    
    mock = mocker.patch(
        "synthex.Synthex._handshake", 
        return_value=mock_handshake_response
    )
    return mock
    
@pytest.fixture(autouse=True)
def isolate_env(tmp_path: Path = Path(".pytest_env_backup")) -> Generator[None, None, None]:
    """
    A pytest fixture that backs up the .env file before each test and restores it afterward.
    It uses a local temporary path to store the backup and ensures the directory is cleaned up after the test.
    
    Args:
        tmp_path (Path): Path used to temporarily store the .env backup.
    
    Yields:
        None
    """
    
    backup_file = tmp_path / ".env.bak"
    tmp_path.mkdir(parents=True, exist_ok=True)

    if os.path.exists(".env"):
        shutil.copy(".env", backup_file)

    yield  # Run the test

    if backup_file.exists():
        shutil.copy(backup_file, ".env")

    # Clean up backup directory
    shutil.rmtree(tmp_path, ignore_errors=True)

@pytest.fixture(autouse=True)
def isolate_anon_id_file(tmp_path: Path = Path(".pytest_anon_id_backup")) -> Generator[None, None, None]:
    """
    A pytest fixture that backs up the file that contains the Synthex anon id before each test and restores 
    it afterward. It uses a local temporary path to store the backup and ensures the directory is cleaned 
    up after the test.
    
    Args:
        tmp_path (Path): Path used to temporarily store the .env backup.
    
    Yields:
        None
    """
    
    backup_file = tmp_path / "anon_id.txt.bak"
    tmp_path.mkdir(parents=True, exist_ok=True)

    if os.path.exists(config.ANON_ID_FILE):
        shutil.copy(config.ANON_ID_FILE, backup_file)

    yield  # Run the test

    if backup_file.exists():
        shutil.copy(backup_file, config.ANON_ID_FILE)

    # Clean up backup directory
    shutil.rmtree(tmp_path, ignore_errors=True)
