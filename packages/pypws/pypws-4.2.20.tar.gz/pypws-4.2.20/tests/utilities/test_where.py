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
            raise FileNotFoundError("The 'pypws' directory was not found in the path hierarchy.")
        current_dir = current_dir.parent

    # Insert the path to the pypws package into sys.path.
    sys.path.insert(0, f'{current_dir}')

from pypws.utilities import where

# Test to get the where element from an empty list.
def test_where_empty_list():
    assert where([], lambda x: x == 1) == []

# Test to get the where element from a list with a single element.
def test_where_single_element():
    assert where([42], lambda x: x == 42) == [42]

# Test to get the where element from a list with multiple unique elements.
def test_where_multiple_elements():
    assert where([3, 4, 5, 11, 2], lambda x: x > 4) == [5,11]

# Test to get the where element from a list where the element is not present.
def test_where_no_elements():
    assert where([3, 4, 5, 11, 2], lambda x: x > 11) == []


