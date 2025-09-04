import pytest
import responses
from pytest_httpx import HTTPXMock

from synthex import Synthex
from synthex.endpoints import API_BASE_URL, GET_JOB_DATA_ENDPOINT
from synthex.models import SuccessResponse
from synthex.exceptions import ValidationError


@pytest.mark.unit
@responses.activate
def test_get_job_data_206_success(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test case for verifying the successful retrieval of job data with a 206 Partial Content status.
    This test mocks an API response for the `GET_JOB_DATA_ENDPOINT` with a 206 status code, indicating
    partial content. It ensures that the `_get_job_data` method of the `Synthex` class correctly handles
    the response and returns a `SuccessResponse` object with the expected attributes.
    Args:
        synthex (Synthex): An instance of the `Synthex` class to test.
    """

    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_JOB_DATA_ENDPOINT("test_job_id")}",
        json={
            "status_code": 206,
            "status": "Partial Content",
            "message": "Jobs data retrieved successfully",
            "data": [
                {
                    "key1a": "value1a",
                    "key2a": "value2a",
                    "key3a": "value3a"
                },
                {
                    "key1b": "value1b",
                    "key2b": "value2b",
                    "key3b": "value3b"
                }
            ]
        },
        status_code=200
    )
    
    job_data = synthex.jobs._get_job_data(job_id="test_job_id") # type: ignore
    assert isinstance(job_data, SuccessResponse), "Job data is not of type SuccessResponse."
    assert job_data.status_code == 206, "Job data status code is not 206."
    assert job_data.status == "Partial Content", "Job data status is not 'Partial Content'."
    
    
@pytest.mark.unit
@responses.activate
def test_get_job_data_200_success(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test case for verifying the successful retrieval of job data, when no data is passed.
    This test simulates a scenario where the API returns a 200 status code
    with a successful response for the `get_job_data` endpoint. It ensures
    that the `_get_job_data` method of the `Synthex` class correctly processes
    the response and returns a `SuccessResponse` object with the expected
    attributes.
    Args:
        synthex (Synthex): An instance of the `Synthex` class.
    """

    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_JOB_DATA_ENDPOINT("test_job_id")}",
        json={
            "status_code": 200,
            "status": "ok",
            "message": "Jobs data retrieved successfully",
            "data": []
        },
        status_code=200
    )
    
    job_data = synthex.jobs._get_job_data(job_id="test_job_id") # type: ignore
    assert isinstance(job_data, SuccessResponse), "Job data is not of type SuccessResponse."
    assert job_data.status_code == 200, "Job data status code is not 200."
    assert job_data.status == "ok", "Job data status is not 'ok'."
    assert job_data.data == [], "Job data is not an empty list."
    
    
@pytest.mark.unit
@responses.activate
def test_get_job_data_validation_error(synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test case for validating the behavior of the `_get_job_data` method when the API response
    contains None data. The `_get_job_data` function should raise a ValidationError in this case.
    Args:
        synthex (Synthex): An instance of the `Synthex` class to test.
    Raises:
        pytest.fail: If the expected `ValidationError` is not raised.
    """

    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_JOB_DATA_ENDPOINT("test_job_id")}",
        json={
            "status_code": 500,
            "status": "Internal Server Error",
            "message": None,
            "data": None
        },
        status_code=200
    )
    
    with pytest.raises(ValidationError):
        synthex.jobs._get_job_data(job_id="test_job_id") # type: ignore