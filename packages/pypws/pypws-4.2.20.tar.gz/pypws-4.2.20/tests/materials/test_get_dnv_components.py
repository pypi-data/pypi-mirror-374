import os
import pathlib
import sys
from pickle import GET

# When running locally the environment variable PYPWS_RUN_LOCALLY needs to be set to True.
# Check if the environment variable is set
PYPWS_RUN_LOCALLY = os.getenv('PYPWS_RUN_LOCALLY')
if PYPWS_RUN_LOCALLY and PYPWS_RUN_LOCALLY.lower() == 'true':
    # Navigate to the PYPWS directory by searching upwards until it is found.
    current_dir = pathlib.Path(__file__).resolve()

    while current_dir.name.lower() != 'package':
        if current_dir.parent == current_dir:  # Check if the current directory is the root directory
            raise FileNotFoundError("The 'pypws' directory was not found in the path hierarchy.")
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')


from pypws.materials import get_dnv_components


def test_get_dnv_components():

    """
    Test to get the list of materials.
        
    """

    # Invoke the method.
    print ('Running get_dnv_components')
    dnv_components = get_dnv_components()

    # Assert if there are no materials returned.
    assert dnv_components is not None, 'No DNV components returned'

    # Print out the list of component names.
    print('Components:')

    for dnv_component in dnv_components:
        print(dnv_component.name)
