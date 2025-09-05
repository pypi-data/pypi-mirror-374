from .api_client import APIClient
from typing import Any, List
import csv
import os
import time
import threading
import logging

from .models import ListJobsResponseModel, JobOutputType, JobOutputSchemaDefinition, GenerateDataResponse, \
    JobStatusResponseModel, SuccessResponse
from .endpoints import LIST_JOBS_ENDPOINT, CREATE_JOB_WITH_SAMPLES_ENDPOINT
from .decorators import auto_validate_methods
from .exceptions import ValidationError
from .config import config
from .endpoints import GET_JOB_DATA_ENDPOINT, GET_JOB_STATUS_ENDPOINT


logger = logging.getLogger(__name__)

@auto_validate_methods
class JobsAPI:
    """
    JobsAPI provides methods for creating, starting and managing jobs.
    """
    
    def __init__(self, client: APIClient):
        self._client: APIClient = client
        
    def list(self, limit: int = 10, offset: int = 0) -> ListJobsResponseModel:
        """
        Retrieve a list of jobs with pagination.
        Args:
            limit (int): The maximum number of jobs to retrieve. Defaults to 10.
            offset (int): The number of jobs to skip before starting to retrieve. Defaults to 0.
        Returns:
            ListJobsResponseModel: A model containing the list of jobs and related metadata.
        """
        
        response = self._client.get(f"{LIST_JOBS_ENDPOINT}?limit={limit}&offset={offset}")
        return ListJobsResponseModel.model_validate(response.data)
    
    @staticmethod
    def _sanitize_output_path(output_path: str, desired_format: JobOutputType) -> str:
        """
        Ensure that the output path is valid, then add the file name to it.
        Args:
            output_path (str): The output path to sanitize.
            format (JobOutputType): The desired output format.
        Returns:
            str: The sanitized output path.
        """
        
        # Determine the correct file extension based on the desired format
        correct_extension = f".{desired_format}"
        
        # Extract the directory and file name from the output path
        directory, file_name = os.path.split(output_path)
        
        # If directory is not provided, use the current working directory
        if not directory:
            # If no directory is provided, use the current working directory
            directory = os.getcwd()
                
        # If a file name is provided, ensure its extension matches the desired format
        if file_name:
            base_name, ext = os.path.splitext(file_name)
            if ext != correct_extension:
                file_name = f"{base_name}{correct_extension}"
        else:
            # If no file name is provided, use a default name with the correct extension
            file_name = config.OUTPUT_FILE_DEFAULT_NAME(desired_format)
        
        # Combine the directory and sanitized file name
        output_path = os.path.join(directory, file_name)
        
        return output_path
    
    def _create_job(
        self, 
        schema_definition: JobOutputSchemaDefinition,
        examples: List[dict[Any, Any]], 
        requirements: List[str],
        number_of_samples: int, 
    ) -> str:
        """
        Create a job with the provided data.
        Args:
            data (dict[str, Any]): The data to create the job with.
        Returns:
            str: The new job ID.
        """
        
        # Validate that each example conforms to the schema definition
        for example in examples:
            if set(example.keys()) != set(schema_definition.keys()):
                raise ValidationError("Example keys do not match schema definition keys.")
        
        # Create data object
        data: dict[str, Any] = {
            "output_schema": schema_definition,
            "examples": examples,
            "requirements": requirements,
            "datapoint_num": number_of_samples
        }
        
        response = self._client.post(f"{CREATE_JOB_WITH_SAMPLES_ENDPOINT}", data=data)
        
        if response.data is None:
            raise ValidationError("Response data is None, expected a valid job ID.")
        return response.data
    
    def _get_job_data(self, job_id: str) -> SuccessResponse[List[dict[Any, Any]]]:
        """
        Fetch data from a job using its ID.
        Args:
            job_id (str): The ID of the job to fetch data from.
        Returns:
            SuccessResponse[List[dict[Any, Any]]]: A SuccessResponse object containing the job data.
        """
        
        response: SuccessResponse[List[dict[Any, Any]]] = self._client.get(GET_JOB_DATA_ENDPOINT(job_id))
                
        if response.data is None:
            raise ValidationError("Response data is None, expected valid data.")
        return response
    
    def _get_data_and_write_to_file(self, job_id: str, output_path: str, output_type: JobOutputType) -> bool:
        """
        Fetch all available datapoints from a job and write them to a file.
        Args:
            job_id (str): The ID of the job to fetch data from.
            output_path (str): The file path where the data should be saved.
            output_type (JobOutputType): The desired output format for the generated data. 
                - "csv": Saves the data to a CSV file.
        Returns:
            bool: True if the data was successfully written to a file.
        """
        
        # Keep fetching data as long as the status code is 206, meaning that there is more data;
        # When the status code changes to 200, that means there is no more data to fetch.
        keep_polling = True
        while keep_polling:
            # Poll every JOB_DATA_POLLING_INTERVAL seconds
            time.sleep(config.JOB_DATA_POLLING_INTERVAL)

            response = self._get_job_data(job_id=job_id)
            keep_polling = response.status_code == 206

            data = response.data
            # Raise an error if the data is not a list
            if not isinstance(data, list):
                raise ValidationError(f"Response data is invalid, expected a list and got: {type(data)}")
            # If data is an empty list (meaning no data is available yet), continue polling
            if len(data) > 0:
                # Check if the file already exists to determine if the header should be written.
                file_exists = os.path.isfile(output_path)
                with open(output_path, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    # Write the header only if the file is being created for the first time.
                    if not file_exists:
                        writer.writeheader()
                    # Append each dict as a row.
                    writer.writerows(data)
                    
                    logger.info(f"{len(data)} datapoints written for job {job_id}")

        logger.info(f"All datapoints for job {job_id} have been written")

        return True

    def generate_data(
        self, 
        schema_definition: JobOutputSchemaDefinition,
        examples: List[dict[Any, Any]], 
        requirements: List[str],
        output_path: str,
        number_of_samples: int, 
        output_type: JobOutputType = "csv",
    ) -> GenerateDataResponse:
        """
        Generates data based on the provided schema definition, examples, and requirements.
        Args:
            schema_definition (dict[Any, Any]): The schema definition that the generated data 
                should conform to.
            examples (List[dict[Any, Any]]): A list of example data points to guide the data 
                generation process.
            requirements (List[str]): A list of specific requirements or constraints for the data 
                generation.
            number_of_samples (int): The number of data samples to generate.
            output_type (JobOutputType): The desired output format for the generated data. 
                - "csv": Saves the data to a CSV file.
            output_path (str): The file path where the generated data should be saved.
        Returns:
            GenerateDataResponse: An object indicating that the job was started successfully.
        """
        
        # Sanitize the output path
        output_path = JobsAPI._sanitize_output_path(output_path, output_type)
                    
        # Create the job
        job_id = self._create_job(
            schema_definition=schema_definition,
            examples=examples,
            requirements=requirements,
            number_of_samples=number_of_samples
        )

        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Start fetching data in a separate thread
        th = threading.Thread(target=self._get_data_and_write_to_file, args=(job_id, output_path, output_type))
        th.start()

        return GenerateDataResponse(
            success=True,
            message=f"Job was started successfully. Output will be saved to '{output_path}'.",
            job_id=job_id
        )

    def status(self, job_id: str) -> JobStatusResponseModel:
        """
        Check the status of a job.
        Args:
            job_id (str): The ID of the job to check the status of.
        Returns:
            JobStatusResponseModel: A model containing the status of the job.
        """

        response = self._client.get(GET_JOB_STATUS_ENDPOINT(job_id))

        return JobStatusResponseModel.model_validate(response.data)
