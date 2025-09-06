# vardescribe

Do you find yourself describing a complex dict or dataframe to an LLM for context?
vardescribe is a simple Python function that prints out the structure, types, and summary statistics of a variable. The output can be easily shared with an LLM or another person for a complete, descriptive overview of that variable.<br />
Example outputs for dict and Pandas dataframe:
```
dict 'my_dict' with 3 keys
        'name'  str [length: 8]
        'age'   scalar int [value: 30]
        'is_student'    scalar bool [value: 0]
```
```
dataframe 'my_df' with 5 rows, 5 columns
        'student_id'    int64   [min:101, max:105, avg:103]
        'major'         object
        'gpa'           float64 [min:3.1, max:3.9, avg:3.5]
        'credits_earned'        int64   [min:55, max:110, avg:80]
        'is_scholarship'        bool
```

## Details
Printed fields include:
* variable name
* shape
* dtype
* summary statistics
* column names of pandas dataframes

Clipboard Integration (Windows only): automatically copies the description to the clipboard for easy pasting into documents, notes, or chat applications.

Currently tested on Windows, Ubuntu

## Getting Started

### Install
```pip install vardescribe```

### Dependencies
Required
* numpy
```pip install numpy```

Optional
* Pandas: Required for describing DataFrame objects. If Pandas is not installed, vardescribe will function correctly for all other types.
```pip install pandas```

### Usage
1. Import: ```from vardescribe import vardescribe```
2. Function call: ```vardescribe(your_variable_name)```

### Example
```
import numpy as np
import pandas as pd
from vardescribe import vardescribe

my_scalar = 2
my_list = [1, 2, 3, 4, 5]
my_numpy_array = np.array([[1, 2], [3, 4]])
my_dict = {
    "name": "John Doe",
    "age": 30,
    "is_student": False
}
student_data = {
    'student_id': [101, 102, 103, 104, 105],
    'major': ['Computer Science', 'Biology', 'Business', 'Art History', 'Computer Science'],
    'gpa': [3.8, 3.2, 3.5, 3.9, 3.1],
    'credits_earned': [90, 65, 80, 110, 55],
    'is_scholarship': [True, False, True, True, False]
}
my_df = pd.DataFrame(student_data)

#describe variables
vardescribe(my_scalar)
print('\n')
vardescribe(my_list)
print('\n')
vardescribe(my_numpy_array)
print('\n')
vardescribe(my_dict)
print('\n')
vardescribe(my_df)
```
### Example output
```
scalar 'my_scalar' int [value: 2]


list 'my_list' size(5) [all int]
        scalar int [value: 1]


ndarray 'my_numpy_array' size(2, 2) int64 [min:1, max:4, avg:2.5]


dict 'my_dict' with 3 keys
        'name'  str [length: 8]
        'age'   scalar int [value: 30]
        'is_student'    scalar bool [value: 0]


dataframe 'my_df' with 5 rows, 5 columns
        'student_id'    int64   [min:101, max:105, avg:103]
        'major'         object
        'gpa'           float64 [min:3.1, max:3.9, avg:3.5]
        'credits_earned'        int64   [min:55, max:110, avg:80]
        'is_scholarship'        bool```
        
## Author
Igor Reidler
igormail@gmail.com

## Version History
* 0.1
    * Initial Release

## License
This project is licensed under the [MIT] License - see the LICENSE.md file for details
