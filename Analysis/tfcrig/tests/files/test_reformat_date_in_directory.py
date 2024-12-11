import unittest

from tfcrig.files import RigFiles


class ReformatDateInDirectoryTestCase(unittest.TestCase):

    def test_reformat_date_in_directory_type_error_none(self):
        """
        Cannot pass None to `reformat_date_in_directory`
        """
        with self.assertRaises(TypeError):
            RigFiles.reformat_date_in_directory(None)

    def test_reformat_date_in_directory_type_error_int(self):
        """
        Cannot pass an integer to `reformat_date_in_directory`
        """
        with self.assertRaises(TypeError):
            RigFiles.reformat_date_in_directory(1)

    def test_reformat_date_in_directory_type_error_int(self):
        """
        Cannot pass an empty string to `reformat_date_in_directory`
        """
        with self.assertRaises(ValueError):
            RigFiles.reformat_date_in_directory("")

    def test_reformat_date_in_directory_string_not_a_date(self):
        """
        The parser `reformat_date_in_directory` is used in a context
        where its string output will be used as a directory name. So if
        it does not change the string, it returns the string it was
        given
        """
        for test_string in ["a", "test", "123_4567_890"]:
            self.assertEqual(
                test_string,
                RigFiles.reformat_date_in_directory(test_string),
            )

    def test_reformat_date_in_directory_string_matches_first_regex(self):
        """
        Various directory names might match the first regex, but the
        parser should always return a formatted date
        """
        for test_date in [
            "1 1 22",
            "01/01/2022",
            "01 01 2022",
            "1/1/22",
            "1 1/2022",
            "01/1/22",
            "1/01/22",
        ]:
            self.assertEqual(
                "2022_01_01",
                RigFiles.reformat_date_in_directory(test_date),
            )

    def test_reformat_date_in_directory_string_matches_second_regex(self):
        """
        Various directory names might match the second regex, but the
        parser should always return a formatted date
        """
        for test_date in [
            "1_1_22",
            "01_01_2022",
            "1_01_2022",
            "1_1_22",
        ]:
            self.assertEqual(
                "2022_01_01",
                RigFiles.reformat_date_in_directory(test_date),
            )


if __name__ == "__main__":
    unittest.main()
