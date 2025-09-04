import pytest
from pytest_httpx import HTTPXMock
from typing import Any

from synthex.endpoints import API_BASE_URL, CREATE_JOB_WITH_SAMPLES_ENDPOINT
from synthex import Synthex
from synthex.exceptions import SynthexError, BadRequestError, AuthenticationError, PaymentRequiredError, \
    RateLimitError, NotFoundError, ServerError, ValidationError


@pytest.mark.unit()
@pytest.mark.parametrize(
    "received_status_code, expected_exception",
    [
        (400, BadRequestError),
        (401, AuthenticationError),
        (402, PaymentRequiredError),
        (404, NotFoundError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, ServerError),
        (501, ServerError),
    ]
)
def test_exceptions(
    synthex: Synthex, httpx_mock: HTTPXMock, generate_data_params: dict[Any, Any],
    received_status_code: int, expected_exception: type[SynthexError]
):
    """
    Test that, whenever an error code is received from the backend, the appropriate Synthex exception is raised.
    Args:
        synthex (Synthex): The Synthex client instance.
        httpx_mock (HTTPXMock): The HTTPX mock instance.
        generate_data_params (dict[Any, Any]): The parameters for generating data.
    """
    
    httpx_mock.add_response(
        method="POST",
        url=f"{API_BASE_URL}/{CREATE_JOB_WITH_SAMPLES_ENDPOINT}",
        json={},
        status_code=received_status_code
    )

    with pytest.raises(expected_exception):
        synthex.jobs._create_job( # type: ignore
            schema_definition=generate_data_params["schema_definition"],
            examples=generate_data_params["examples"],
            requirements=generate_data_params["requirements"],
            number_of_samples=generate_data_params["number_of_samples"],
        )