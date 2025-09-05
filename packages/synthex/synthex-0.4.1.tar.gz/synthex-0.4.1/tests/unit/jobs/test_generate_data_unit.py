from typing import Any
import pytest

from synthex import Synthex
from synthex.exceptions import ValidationError
        

@pytest.mark.unit
def test_generate_data_schema_definition_wrong_type(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test case for validating the behavior of the `generate_data` method when an invalid 
    `schema_definition` is provided. This test ensures that a `ValidationError` is raised when 
    the `schema_definition` parameter has an incorrect type (e.g., an integer instead of 
    the expected type).
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` 
            method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """

    with pytest.raises(ValidationError):
        synthex.jobs.generate_data(
            # Invalid argument type for schema_definition
            schema_definition={
                "question": {
                    "datatype": "string" #type: ignore
                },
                "option-a": {
                    "type": "string"
                }
            },
            examples=generate_data_params["examples"],
            requirements=generate_data_params["requirements"],
            number_of_samples=generate_data_params["number_of_samples"],
            output_type=generate_data_params["output_type"],
            output_path=generate_data_params["output_path"]
        )

@pytest.mark.unit
def test_generate_data_examples_wrong_type(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test case for validating the behavior of the `generate_data` method when an invalid 
    `examples` is provided. This test ensures that a `ValidationError` is raised when the 
    `examples` parameter has an incorrect type (e.g., an integer instead of the 
    expected type).
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` 
            method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """
    
    with pytest.raises(ValidationError):
        synthex.jobs.generate_data(
            schema_definition=generate_data_params["schema_definition"],
            # Invalid argument type for examples
            examples=1, #type: ignore
            requirements=generate_data_params["requirements"],
            number_of_samples=generate_data_params["number_of_samples"],
            output_type=generate_data_params["output_type"],
            output_path=generate_data_params["output_path"]
        )

@pytest.mark.unit
def test_generate_data_examples_schema_definition_mismatch(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test case for validating the behavior of the `generate_data` method when an invalid 
    `examples` is provided. This test ensures that a `ValidationError` is raised when the 
    `examples` parameter is inconsistent with the `schema_definition` parameter (e.g.,
    the `examples` parameter contains fields that are not present in the `schema_definition`).
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` 
            method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """
    
    with pytest.raises(ValidationError):
        synthex.jobs.generate_data(
            schema_definition=generate_data_params["schema_definition"],
            # Invalid argument type for examples
            examples=[{
                "question": "Random question",
                "option-a": "12.0 L",
                "option-b": "24.0 L",
                "option-c": "6.0 L",
                "option-d": "3.0 L",
                # "Answer" field is missing
            }],
            requirements=generate_data_params["requirements"],
            number_of_samples=generate_data_params["number_of_samples"],
            output_type=generate_data_params["output_type"],
            output_path=generate_data_params["output_path"]
        )

@pytest.mark.unit
def test_generate_data_requirements_wrong_type(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test case for validating the behavior of the `generate_data` method when an invalid 
    `requirements` is provided. This test ensures that a `ValidationError` is raised when 
    the `requirements` parameter has an incorrect type (e.g., a string instead of the 
    expected list of strings).
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` 
            method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """
    
    with pytest.raises(ValidationError):
        synthex.jobs.generate_data(
            schema_definition=generate_data_params["schema_definition"],
            examples=generate_data_params["examples"],
            # Invalid argument type for requirements
            requirements="Sample requirement", #type: ignore
            number_of_samples=generate_data_params["number_of_samples"],
            output_type=generate_data_params["output_type"],
            output_path=generate_data_params["output_path"]
        )

@pytest.mark.unit
def test_generate_data_num_of_samples_wrong_type(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test case for validating the behavior of the `generate_data` method when an invalid 
    `number_of_samples` is provided. This test ensures that a `ValidationError` is raised when 
    the `number_of_samples` parameter has an incorrect type (e.g., a string instead of 
    the expected integer).
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """
    
    with pytest.raises(ValidationError):
        synthex.jobs.generate_data(
            schema_definition=generate_data_params["schema_definition"],
            examples=generate_data_params["examples"],
            requirements=generate_data_params["requirements"],
            # Invalid argument type for number_of_samples
            number_of_samples="test", #type: ignore
            output_type=generate_data_params["output_type"],
            output_path=generate_data_params["output_path"]
        )
        
@pytest.mark.unit
def test_generate_data_output_type_wrong_type(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test case for validating the behavior of the `generate_data` method when an invalid 
    `output_type` is provided. This test ensures that a `ValidationError` is raised when the 
    `output_type` parameter has an incorrect type (e.g., an unallowed string).
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """
    
    with pytest.raises(ValidationError):
        synthex.jobs.generate_data(
            schema_definition=generate_data_params["schema_definition"],
            examples=generate_data_params["examples"],
            requirements=generate_data_params["requirements"],
            number_of_samples=generate_data_params["number_of_samples"],
            # Invalid argument type for output_type
            output_type="ttt", #type: ignore
            output_path=generate_data_params["output_path"]
        )
        
@pytest.mark.unit
def test_generate_data_output_path_wrong_type(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test case for validating the behavior of the `generate_data` method when an invalid 
    `output_path` is provided. This test ensures that a `ValidationError` is raised when 
    the `output_path` parameter has an incorrect type (e.g., an integer instead of 
    the expected type).
    Args:
        synthex (Synthex): An instance of the Synthex class used to invoke the `generate_data` 
            method.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters 
    """
    
    with pytest.raises(ValidationError):
        synthex.jobs.generate_data(
            schema_definition=generate_data_params["schema_definition"],
            examples=generate_data_params["examples"],
            requirements=generate_data_params["requirements"],
            number_of_samples=generate_data_params["number_of_samples"],
            output_type=generate_data_params["output_type"],
            # Invalid argument type for output_type
            output_path=1 #type: ignore
        )
