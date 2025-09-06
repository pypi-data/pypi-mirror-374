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

from pypws.utilities import single_or_default

# Test to get the single or default element from an empty list.
def test_single_or_default_empty_list():
    assert single_or_default([], lambda x: x == True) is None

# Test to get the single or default element from a list where multiple elements match the predicate.
def test_single_or_default_multiple_matches():
    assert single_or_default([1, 2, 3, 3, 5], lambda x: x == 3) is None

# Test to get the single or default element from a list where the element is equal to a value.
def test_single_or_default_equal_to_a_value():
    assert single_or_default([1, 2, 3, 4, 5], lambda x: x == 3) == 3

# Test to get the single or default element from a list where the element is not equal to a value.
def test_single_or_default_not_equal_to_a_value():
    assert single_or_default([1, 2, 3, 4, 5], lambda x: x != 4) is None

# Test to get the single or default element from a list where the element is not present.    
def test_single_or_default_the_value_is_not_present():
    assert single_or_default([1, 2, 3, 4, 5], lambda x: x == 6) is None

# Test to get the single or default element from a list where the element is not present and the default value is given.
def test_single_or_default_the_value_default_given():
    assert single_or_default([1, 2, 3, 4, 5], lambda x: x == 6, 0) == 0