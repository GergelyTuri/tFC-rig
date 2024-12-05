import unittest

from tfcrig.files import extract_cohort_mouse_pairs


class ExtractCohortMousePairsTestCase(unittest.TestCase):

    def test_extract_cohort_mouse_pairs_type_error_none(self):
        """
        Cannot pass None to `extract_cohort_mouse_pairs`
        """
        with self.assertRaises(TypeError):
            extract_cohort_mouse_pairs(None)

    def test_extract_cohort_mouse_pairs_type_error_int(self):
        """
        Cannot pass an integer to `extract_cohort_mouse_pairs`
        """
        with self.assertRaises(TypeError):
            extract_cohort_mouse_pairs(1)

    def test_extract_cohort_mouse_pairs_type_error_int(self):
        """
        Cannot pass an empty string to `extract_cohort_mouse_pairs`
        """
        with self.assertRaises(ValueError):
            extract_cohort_mouse_pairs("")

    def test_extract_cohort_mouse_pairs_includes_datetime(self):
        """
        Extracting cohort, mouse pairs from a file name requires it to
        have already had the date time and file extension portions
        removed
        """
        with self.assertRaises(ValueError):
            extract_cohort_mouse_pairs("106_1_106_2_2024-11-15_15-48-17.json")

    def test_extract_cohort_mouse_pairs_partial_valid_input(self):
        """
        Can only operate on strings that consist only of cohort, mouse pairs
        """
        with self.assertRaises(ValueError):
            extract_cohort_mouse_pairs("106_1_106_2_somethingElse")

    def test_extract_cohort_mouse_pairs_valid_input(self):
        self.assertEqual(
            extract_cohort_mouse_pairs("106_1_106_2_"),
            ["106_1_", "106_2_"]
        )

    def test_extract_cohort_mouse_pairs_valid_input_longer(self):
        self.assertEqual(
            extract_cohort_mouse_pairs("106_1_106_2_107_1_107_2_"),
            ["106_1_", "106_2_", "107_1_", "107_2_"]
        )

if __name__ == "__main__":
    unittest.main()
