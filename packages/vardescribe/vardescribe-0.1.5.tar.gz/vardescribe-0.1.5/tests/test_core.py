import pytest
import numpy as np
import pandas as pd
from src.vardescribe.core import vardescribe

def assert_output_contains(output: str, expected_terms: list):
    # Asserts that every term in the expected_terms list is present as a substring in the given output string.
    for term in expected_terms:
        assert term in output, f"Expected to find '{term}' in the output, but it was missing."

def test_vardescribe_scalar(capsys):
    """Tests that scalar description is both printed and returned correctly."""
    my_scalar = 2
    # Capture the returned value
    report = vardescribe(my_scalar)
    
    # Check the printed output
    captured_output = capsys.readouterr().out
    expected_terms = [
        "scalar",
        "my_scalar",
        "int",
        "value: 2"
    ]
    assert_output_contains(captured_output, expected_terms)
    
    # Check the returned value
    assert_output_contains(report, expected_terms)

def test_vardescribe_list(capsys):
    """Tests that list description is both printed and returned correctly."""
    my_list = [1, 2, 3, 4, 5]
    # Capture the returned value
    report = vardescribe(my_list)

    # Check the printed output
    captured_output = capsys.readouterr().out
    expected_terms = [
        "list",
        "my_list",
        "size(5)",
        "all int"
    ]
    assert_output_contains(captured_output, expected_terms)
    
    # Check the returned value
    assert_output_contains(report, expected_terms)

def test_vardescribe_numpy_array(capsys):
    """Tests that numpy array description is both printed and returned correctly."""
    my_numpy_array = np.array([[1, 2], [3, 4]], dtype=np.int64)
    # Capture the returned value
    report = vardescribe(my_numpy_array)
    
    # Check the printed output
    captured_output = capsys.readouterr().out
    expected_terms = [
        "ndarray",
        "my_numpy_array",
        "size(2, 2)",
        "int64",
        "min:1",
        "max:4",
        "avg:2.5"
    ]
    assert_output_contains(captured_output, expected_terms)

    # Check the returned value
    assert_output_contains(report, expected_terms)

def test_vardescribe_dict(capsys):
    """Tests that dict description is both printed and returned correctly."""
    my_dict = {
        "name": "John Doe",
        "age": 30,
        "is_student": False
    }
    # Capture the returned value
    report = vardescribe(my_dict)

    # Check the printed output
    captured_output = capsys.readouterr().out
    expected_terms = [
        "dict",
        "my_dict",
        "3 keys",
        "'name'",
        "'age'",
        "'is_student'"
    ]
    assert_output_contains(captured_output, expected_terms)

    # Check the returned value
    assert_output_contains(report, expected_terms)

def test_vardescribe_dataframe(capsys):
    """Tests that DataFrame description is both printed and returned correctly."""
    student_data = {
        'student_id': [101, 102, 103, 104, 105],
        'major': ['Computer Science', 'Biology', 'Business', 'Art History', 'Computer Science'],
        'gpa': [3.8, 3.2, 3.5, 3.9, 3.1]
    }
    my_df = pd.DataFrame(student_data)
    # Capture the returned value
    report = vardescribe(my_df)

    # Check the printed output
    captured_output = capsys.readouterr().out
    expected_terms = [
        "dataframe",
        "my_df",
        "5 rows",
        "3 columns",
        "'student_id'",
        "'major'",
        "'gpa'",
        "min:3.1",
        "max:3.9"
    ]
    assert_output_contains(captured_output, expected_terms)

    # Check the returned value
    assert_output_contains(report, expected_terms)