from typing import Callable


# General
API_BASE_URL: str = "https://compute.tanaos.com"
PING_ENDPOINT = "/"
HANDSHAKE_ENDPOINT = "handshake"

# User
GET_CURRENT_USER_ENDPOINT = "user"

# Credits
GET_CREDITS_ENDPOINT = "user/credits"

# Jobs
LIST_JOBS_ENDPOINT = "jobs"
CREATE_JOB_WITH_SAMPLES_ENDPOINT = "jobs/with-samples"
GET_JOB_DATA_ENDPOINT: Callable[[str], str] = lambda job_id: f"jobs/with-samples/{job_id}/data"
GET_JOB_STATUS_ENDPOINT: Callable[[str], str] = lambda job_id: f"jobs/{job_id}/status"