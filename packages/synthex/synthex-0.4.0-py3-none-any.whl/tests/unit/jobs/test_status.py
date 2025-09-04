import pytest
import responses
from pytest_httpx import HTTPXMock

from synthex import Synthex
from synthex.endpoints import API_BASE_URL, GET_JOB_STATUS_ENDPOINT
from synthex.models import JobStatusResponseModel
from synthex.exceptions import ValidationError


@responses.activate
@pytest.mark.unit
def test_status_success(
    short_lived_synthex: Synthex, httpx_mock: HTTPXMock
):
    """
    Test the `status` method of the `jobs` module in the `Synthex` class. This test verifies that the `status` method 
    correctly retrieves the job status and progress when the API response indicates success.
    Args:
        synthex (Synthex): An instance of the `Synthex` class to be tested.
    """
    
    job_id = "123"
    test_status = "In Progress"
    test_progress = 0.5
    
    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_JOB_STATUS_ENDPOINT(job_id)}",
        json={
            "status_code": 200,
            "status": "success",
            "message": "Job status retrieved successfully",
            "data": {
                "status": test_status,
                "progress": test_progress
            }
        },
        status_code=200
    )
    
    # Artificially set the current job ID to "job_id" for testing purposes.
    short_lived_synthex.jobs._current_job_id = job_id # type: ignore
    
    status = short_lived_synthex.jobs.status()
    assert isinstance(status, JobStatusResponseModel), "Status should be of type JobStatusResponseModel"
    assert status.status == test_status, f"Status should be {test_status}"
    assert status.progress == test_progress, f"Progress should be {test_progress}"
    
    
@responses.activate
@pytest.mark.unit
def test_status_no_running_job_failure(
    short_lived_synthex: Synthex,
):
    """
    This test verifies that a `ValidationError` is raised when attempting to 
    check the status of jobs through `JobsAPI.status` while no job is currently running. If the exception 
    is not raised, the test will fail with an appropriate error message.
    Args:
        synthex (Synthex): An instance of the `Synthex` class to be tested.
    """
    
    with pytest.raises(ValidationError):
        short_lived_synthex.jobs.status()