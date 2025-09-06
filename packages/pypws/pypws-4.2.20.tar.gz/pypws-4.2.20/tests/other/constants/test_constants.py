import os
import pathlib
import sys

# When running locally the environment variable PYPWS_RUN_LOCALLY needs to be set to True.
# Check if the environment variable is set
PYPWS_RUN_LOCALLY = os.getenv('PYPWS_RUN_LOCALLY')
if PYPWS_RUN_LOCALLY and PYPWS_RUN_LOCALLY.lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        if current_dir.parent == current_dir:  # Check if the current directory is the root directory
            raise FileNotFoundError("The 'package' directory was not found in the path hierarchy.")
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.constants import PWS_CLIENT_ID, REST_API_URI


def test_phast_client_id():
    assert PWS_CLIENT_ID == 'a8dd2eef-e244-480f-af9a-788cf43a2f0b'

def test_analytics_rest_api_uri():
     print('Running test_analytics_rest_api_uri')
     assert REST_API_URI == 'https://plantwebservices.dnv.com/api/'