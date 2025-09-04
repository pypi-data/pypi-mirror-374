import responses
import pytest
from pytest_httpx import HTTPXMock

from synthex import Synthex
from synthex.endpoints import API_BASE_URL, GET_CREDITS_ENDPOINT
from synthex.models import CreditResponseModel
from synthex.exceptions import NotFoundError, AuthenticationError


@pytest.mark.unit
@responses.activate
def test_credits_success(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    This test verifies that the `credits` method in the `Synthex` class correctly retrieves credit information
    from the API and maps it to a `CreditResponseModel` instance.
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """

    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_CREDITS_ENDPOINT}/",
        json={
            "status_code": 200,
            "status": "success",
            "message": "Credits retrieved successfully",
            "data": {
                "amount": 100,
                "currency": "USD",
            }
        },
        status_code=200
    )

    credits_info = synthex.credits()

    assert isinstance(credits_info, CreditResponseModel), "Credits info is not of type CreditResponseModel."
    assert credits_info.amount == 100, "Credits amount is not 100."
    assert credits_info.currency == "USD", "Credits currency is not USD."

@pytest.mark.unit
@responses.activate
def test_credits_401_failure(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test case for verifying the behavior of the `credits` method when the API responds with a 401 Unauthorized error.
    This test simulates an unauthorized API response by mocking the GET request to the credits endpoint. It ensures that
    the `credits` method raises an `AuthenticationError` when the API returns a 401 status code.
    Args:
        synthex (Synthex): An instance of the Synthex class to test.
    """

    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_CREDITS_ENDPOINT}/",
        json={"error": "unauthorized"},
        status_code=401
    )

    with pytest.raises(AuthenticationError):
        synthex.credits()


@pytest.mark.unit
@responses.activate
def test_credits_404_failure(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test case for handling a 404 Not Found error when attempting to retrieve credits.
    This test simulates a scenario where the API endpoint for fetching credits returns a 404 status code. 
    It verifies that the `synthex.credits()` method raises a `NotFoundError` exception
    in response to the error.
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """

    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_CREDITS_ENDPOINT}/",
        json={
            "status_code": 404,
            "status": "error",
            "message": "Not found",
            "details": None
        },
        status_code=404
    )

    with pytest.raises(NotFoundError):
        synthex.credits()