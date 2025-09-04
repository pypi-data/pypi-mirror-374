import pytest
import responses
from typing import Any
from pathlib import Path
import csv
from pytest_httpx import HTTPXMock

from synthex import Synthex
from synthex.endpoints import API_BASE_URL, GET_JOB_DATA_ENDPOINT


@pytest.mark.unit
@responses.activate
def test_get_data_and_write_to_file_success(tmp_path: Path, synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test case for validating the behavior of the `test_get_data_and_write_to_file_success` method. This method should
    successfully fetch data from a job and write it to a CSV file. The test checks if the file is created and
    verifies the contents of the file against the expected data.
    Args:
        tmp_path (Path): A temporary directory path for the test.
        synthex (Synthex): An instance of the `Synthex` class to test.
    Raises:
        pytest.fail: If the expected `ValidationError` is not raised.
    """
    
    line_a = {
        "key1": "value1a",
        "key2": "value2a",
        "key3": "value3a"
    }
    
    line_b = {
        "key1": "value1b",
        "key2": "value2b",
        "key3": "value3b"
    }
    
    data: dict[str, Any] = {
        "status_code": 206,
        "status": "Partial Content",
        "message": "Jobs data retrieved successfully",
        "data": [
            line_a,
            line_b
        ]
    }
    
    # First response returns data
    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_JOB_DATA_ENDPOINT("test_job_id")}",
        json=data,
        status_code=200
    )
    
    # Second response returns more data
    httpx_mock.add_response(
        method="GET",
        url=f"{API_BASE_URL}/{GET_JOB_DATA_ENDPOINT("test_job_id")}",
        json=data,
        status_code=200
    )
    
    # Third response does not return any more data
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
    
    output_file = f"{tmp_path}/output.csv"
    
    synthex.jobs._get_data_and_write_to_file( # type: ignore
        "test_job_id", output_file, "csv"
    )
    
    # Check if the file was created
    assert Path(output_file).exists(), "Output file was not created"
    
    # Check the contents of the file
    with open(output_file, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert len(rows) == 4, "Incorrect number of rows in the output file"
        assert rows[0] == line_a, "First row data is incorrect"
        assert rows[1] == line_b, "Second row data is incorrect"
        assert reader.fieldnames == list(line_a.keys()), "Header is incorrect"
        
        
@pytest.mark.unit
@responses.activate
def test_get_data_and_write_to_file_no_data(tmp_path: Path, synthex: Synthex, httpx_mock: HTTPXMock):
    """
    Test the `_get_data_and_write_to_file` method when no data is returned from the API.
    This test verifies that when the API response contains no data, the method does not
    create an output file.
    Args:
        tmp_path (Path): A temporary directory path provided by pytest for creating temporary files during the test.
        synthex (Synthex): An instance of the Synthex class being tested.
    """
    
    # Response does not return any data
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
    
    output_file = f"{tmp_path}/output.csv"
    
    synthex.jobs._get_data_and_write_to_file( # type: ignore
        "test_job_id", output_file, "csv"
    )
    
    # No output file should be created
    assert not Path(output_file).exists(), "Output file was created, although it should not have been"