import pytest
from unittest import mock

from synthex.models import JobOutputType
from synthex.config import config
from synthex.jobs_api import JobsAPI


@pytest.mark.unit
@pytest.mark.parametrize(
    "output_path, desired_format, expected_path",
    [
        ("results/output", "csv", "results/output.csv"),
        ("results/output.json", "csv", "results/output.csv"),
        ("results/output.csv", "csv", "results/output.csv"),
        ("", "csv", config.OUTPUT_FILE_DEFAULT_NAME("csv")),
    ]
)
def test_sanitize_output_path(
    output_path: str,
    desired_format: JobOutputType,
    expected_path: str
):
    """
    Test the `_sanitize_output_path` method of the `Synthex` class.
    This test verifies that the `_sanitize_output_path` method correctly processes
    the given output path and desired format, returning the expected sanitized path.
    Args:
        synthex (Synthex): An instance of the `Synthex` class.
        output_path (str): The output path to be sanitized.
        desired_format (JobOutputType): The desired output format.
        expected_path (str): The expected sanitized output path.
    """
    
    with mock.patch("os.getcwd", return_value=""):
        sanitized = JobsAPI._sanitize_output_path( # type: ignore
            output_path, desired_format
        )
        assert sanitized == expected_path