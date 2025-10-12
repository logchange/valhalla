# Test Execution Instructions

To run tests in this project, use the following command:
```bash
python -m unittest discover -s test -t test -p '*_test.py'
```

# Test template

When creating a new test, please use the following template:
```python
import unittest

class SomeClassTest(unittest.TestCase):
    
    def test_some_method(self, mock_run):
        # given:
        ...
        # when:
        ...
        # then:
        ...

```