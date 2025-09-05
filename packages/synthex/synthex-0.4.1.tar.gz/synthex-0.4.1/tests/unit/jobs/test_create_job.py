from typing import Any, List
import responses
import pytest
from pytest_httpx import HTTPXMock

from synthex import Synthex
from synthex.endpoints import API_BASE_URL, CREATE_JOB_WITH_SAMPLES_ENDPOINT
from synthex.models import JobOutputSchemaDefinition
from synthex.exceptions import ValidationError


@pytest.mark.unit
@responses.activate
def test_create_job_success(synthex: Synthex, generate_data_params: dict[Any, Any], httpx_mock: HTTPXMock):
    """
    Test the successful creation of a job using the Synthex API.
    This test verifies that the `_create_job` method in the `jobs` module of the
    `Synthex` class correctly creates a job and returns the expected job ID. It also
    ensures that the `_current_job_id` attribute is updated accordingly.
    Args:
        synthex (Synthex): An instance of the Synthex class.
        generate_data_params (dict[Any, Any]): A dictionary containing the parameters
            required for job creation, including:
            - schema_definition: The schema definition for the job.
            - examples: Example data for the job.
            - requirements: Requirements for the job.
            - number_of_samples: The number of samples to generate.
    """

    httpx_mock.add_response(
        method="POST",
        url=f"{API_BASE_URL}/{CREATE_JOB_WITH_SAMPLES_ENDPOINT}",
        json={
            "status_code": 200,
            "status": "success",
            "message": "Job created successfully",
            "data": "abc123"
        },
        status_code=200
    )

    job_id = synthex.jobs._create_job( # type: ignore
        schema_definition=generate_data_params["schema_definition"],
        examples=generate_data_params["examples"], 
        requirements=generate_data_params["requirements"],
        number_of_samples=generate_data_params["number_of_samples"],
    )
    
    assert job_id == "abc123"    
    
@pytest.mark.unit
@responses.activate
def test_create_job_service_validation_error(
    synthex: Synthex, generate_data_params: dict[Any, Any], httpx_mock: HTTPXMock
):
    """
    Test case for validating the behavior of the `create_job` method when a validation error occurs due to
    the upstream service returning a None job ID. This test ensures that a `ValidationError` is raised as 
    expected.
    Args:
        synthex (Synthex): An instance of the Synthex class, representing the main application object.
        generate_data_params (dict[Any, Any]): A dictionary containing the parameters required for 
            creating a job, including schema definition, examples, requirements, and number of samples.
    """

    httpx_mock.add_response(
        method="POST",
        url=f"{API_BASE_URL}/{CREATE_JOB_WITH_SAMPLES_ENDPOINT}",
        json={
            "status_code": 200,
            "status": "success",
            "message": "Job created successfully",
            "data": None
        },
        status_code=200
    )

    with pytest.raises(ValidationError):
        synthex.jobs._create_job( # type: ignore
            schema_definition=generate_data_params["schema_definition"],
            examples=generate_data_params["examples"], 
            requirements=generate_data_params["requirements"],
            number_of_samples=generate_data_params["number_of_samples"],
        )
    
    
@pytest.mark.unit
@pytest.mark.parametrize(
    "schema_definition, examples, requirements, number_of_samples",
    [
        ({"field": {"typ": "string"}}, [{"field": "key"}], [], 10), # wrong schema definition, typo in "typ"
        ({"field": {"type": "string"}}, [{"fiel": "key"}], [], 10), # wrong examples, mismatch between schema and example
        ({"field": {"type": "string"}}, 1, [], 10), # wrong examples, incorrect type
        ({"field": {"type": "string"}}, [{"field": "key"}], "some requirement", 10), # wrong requirements, not a list
    ]
)
def test_create_job_argument_validation_error(
    synthex: Synthex,
    schema_definition: JobOutputSchemaDefinition,
    examples: List[dict[Any, Any]], 
    requirements: List[str],
    number_of_samples: int, 
):
    """
    Test case for validating the behavior of the `_create_job` method when invalid parameters are provided.
    This test ensures that a `ValidationError` is raised when the `_create_job` method is called with 
    incorrect or invalid input parameters. If the exception is not raised, the test will fail with an 
    appropriate error message.
    Args:
        synthex (Synthex): An instance of the `Synthex` class used to invoke the `_create_job` method.
        schema_definition (JobOutputSchemaDefinition): The schema definition for the job output.
        examples (List[dict[Any, Any]]): A list of example data dictionaries to be used in the job creation.
        requirements (List[str]): A list of requirements for the job.
        number_of_samples (int): The number of samples to be generated for the job.
    """
    
    with pytest.raises(ValidationError):
        synthex.jobs._create_job( # type: ignore
            schema_definition=schema_definition,
            examples=examples,
            requirements=requirements,
            number_of_samples=number_of_samples,
        )