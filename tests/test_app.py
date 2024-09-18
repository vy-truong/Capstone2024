# tests/test_app.py
import unittest
from main.app import get_number_of_employees  # Ensure this import is correct

class TestAppFunctions(unittest.TestCase):

    def test_get_number_of_employees(self):
        result = get_number_of_employees(6)
        self.assertEqual(result, 6, "The number of employees should be 6")

if __name__ == "__main__":
    unittest.main()
