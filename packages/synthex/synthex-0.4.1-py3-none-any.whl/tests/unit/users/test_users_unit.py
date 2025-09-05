import responses
import pytest
from pytest_httpx import HTTPXMock

from synthex import Synthex
from synthex.endpoints import API_BASE_URL, GET_CURRENT_USER_ENDPOINT
from synthex.models import UserResponseModel
from synthex.exceptions import NotFoundError, AuthenticationError


@pytest.mark.unit
@responses.activate
def test_me_success(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test the `me` method of the `users` module in the `Synthex` class.
    This test verifies that the `me` method correctly retrieves and parses
    the current user's information from the API response.
    Steps:
    1. Mock an HTTP GET request to the endpoint with a successful response.
    2. Parse the response into a `UserResponseModel` object.
    3. Assert that the returned object has the expected attributes and values.
    Args:
        synthex (Synthex): An instance of the Synthex class to test.
    """
    
    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_CURRENT_USER_ENDPOINT}",
        json={
            "status_code": 200,
            "status": "success",
            "message": "User retrieved successfully",
            "data": {
                "id": "abc123",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@gmail.com",
                "is_verified": True   
            }
        },
        status_code=200
    )

    user = synthex.users.me()

    assert isinstance(user, UserResponseModel), "User info is not of type UserResponseModel."
    assert user.id == "abc123", "User ID does not match the expected value."
    assert user.first_name == "John", "User first name does not match the expected value."
    assert user.last_name == "Doe", "User last name does not match the expected value."
    assert user.email == "john.doe@gmail.com", "User email does not match the expected value."
    assert user.is_verified is True, "User verification status does not match the expected value."
    

@pytest.mark.unit
@responses.activate
def test_me_401_failure(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test that the `me` method of the `users` module in the `Synthex` class
    raises an `AuthenticationError` when the API responds with a 401 
    Unauthorized error.
    Steps:
    1. Mock an HTTP GET request to the endpoint with a 401 status code and 
       an error message indicating unauthorized access.
    2. Assert that calling `synthex.users.me()` raises an `AuthenticationError`.
    Args:
        synthex (Synthex): An instance of the Synthex class to test.
    """
    
    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_CURRENT_USER_ENDPOINT}",
        json={"error": "unauthorized"},
        status_code=401
    )

    with pytest.raises(AuthenticationError):
        synthex.users.me()


@pytest.mark.unit
@responses.activate
def test_me_404_failure(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test case for handling a 404 Not Found error when retrieving the current user.
    This test simulates a scenario where the API returns a 404 response for the
    "me" endpoint. It ensures that the `synthex.users.me()` method
    raises a `NotFoundError` exception when the endpoint is not found.
    Args:
        synthex (Synthex): An instance of the Synthex client to test.
    """
    
    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_CURRENT_USER_ENDPOINT}",
        json={
            "status_code": 404,
            "status": "error",
            "message": "Not found",
            "details": None
        },
        status_code=404
    )

    with pytest.raises(NotFoundError):
        synthex.users.me()