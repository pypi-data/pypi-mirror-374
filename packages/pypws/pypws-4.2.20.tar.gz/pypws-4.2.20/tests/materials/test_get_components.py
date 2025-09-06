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


from pypws.materials import get_components


def test_get_components():

    """
    Test to get the list of components.
        
    """

    # Invoke the method for DNV components.
    print ('Running get_components for DNV components')
    components = get_components(1)

    # Assert if there are no components returned.
    assert components is not None, 'No components returned'

    # Print out the list of component names.    
    print('DNV components:')

    for component in components:
        print(f'{component.name}, {component.id}')

    # Invoke the method for DIPPR components.
    print ('Running get_components for DIPPR components')
    components = get_components(2)

    # Assert if there are no DIPPR components returned.
    assert components is not None, 'No DIPPR components returned'

    # Print out the list of component names.    
    print('DIPPR components:')

    for component in components:
        print(f'{component.name}, {component.id}')
