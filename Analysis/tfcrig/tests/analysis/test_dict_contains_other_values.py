import unittest

from tfcrig.analysis import dict_contains_other_values


class DictContainsOtherValuesTestCase(unittest.TestCase):

    def test_dict_contains_other_values_type_error_none(self):
        """
        Cannot pass None to `dict_contains_other_values`
        """
        with self.assertRaises(TypeError):
            dict_contains_other_values(None, (dict, list, str))

    def test_dict_contains_other_values_type_error_int(self):
        """
        Cannot pass an integer to `dict_contains_other_values`
        """
        with self.assertRaises(TypeError):
            dict_contains_other_values(1, (dict, list, str))

    def test_dict_contains_other_values_type_error_string(self):
        """
        Cannot pass a string to `dict_contains_other_values`
        """
        with self.assertRaises(TypeError):
            dict_contains_other_values("a", (dict, list, str))

    def test_dicts_dont_contain_other_values(self):
        """
        Test a list of pairs of dictionaries and sets of types that
        do not contain any other values
        """
        for d, types in [
            ({"key": "value"}, (dict, list, str)),
            ({"key": ["value"]}, (dict, list, str)),
            ({"key": {"key": "value"}}, (dict, list, str)),
        ]:
            self.assertFalse(dict_contains_other_values(d, types))

    def test_dicts_contain_other_values(self):
        """
        Test a list of pairs of dictionaries and sets of types that
        do contain other values
        """

        for d, types in [
            ({"key": "value"}, (dict, list)),
            ({"key": ["value"]}, (dict, str)),
            ({"key": {"key": "value"}}, (list, str)),
        ]:
            self.assertTrue(dict_contains_other_values(d, types))


if __name__ == "__main__":
    unittest.main()
