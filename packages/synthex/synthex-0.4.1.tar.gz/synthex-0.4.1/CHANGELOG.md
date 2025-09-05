## Release v0.4.1 - September 4, 2025

### Added

- Added a `job_id` field to the response of the `generate_data` method.

### Modified

- Updated the `status` method in `JobsAPI` to accept a `job_id` parameter, allowing users to check the status of any job by its ID.
- Changed the `generate_data` method to initiate data fetching in a separate thread, enabling asynchronous job processing.

## Release v0.4.0 - September 3, 2025

First release.