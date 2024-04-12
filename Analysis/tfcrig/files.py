import os
import re

from dataclasses import dataclass

from tfcrig.notebook import builtin_print

DATETIME_REGEX = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
"""
Regex matching for a datetime of the format `YYYY-MM-DD_HH-MM-SS` which
is included in the file names generated during data collection
"""

BAD_DATE_REGEX_1 = r"(\d{1,2})[ \/](\d{1,2})[ \/](\d{2,4})"
"""
Possible date format in Google Drive folder names
"""
BAD_DATE_REGEX_2 = r"(\d{1,2})[_](\d{1,2})[_](\d{2,4})"
"""
Possible date format in Google Drive folder names
"""


def extract_exp_mouse_pairs(exp_mouse_blob: str) -> list[str]:
    """
    Define a recursive function that helps extract sets of
    `{experiment_id}_{mouse_id}_` from a file name. It accepts the
    front portion of a session file name and returns a list of
    these sets
    """
    pattern = r"\d+[_-]\d+[_-]"
    string_match = re.search(pattern, exp_mouse_blob)

    if string_match:
        first_pair = string_match.group()
        rest_of_string = exp_mouse_blob[string_match.end():]
        return [first_pair] + extract_exp_mouse_pairs(rest_of_string)
    return []


@dataclass
class RigFiles:
    """
    Given an absolute file path to a set of project data generated by
    a trace fear conditioning rig, provide a set of helper functions to
    clean the data before an analysis.
    """

    data_root: str = "/gdrive/Shareddrives/Turi_lab/Data/aging_project/"
    dry_run: bool = True

    def check(self) -> None:
        """
        Performs a set of checks. The `clean` public method on this
        class would, when applicable, fix what these checks discover
        """
        self._are_data_files_named_correctly()

    def clean(self) -> None:
        """
        Runs through a set of ways to clean the data. If `dry_run` is
        `True` it will only print out what it _would_ have cleaned,
        which can be useful as a safety check before modifying any
        data
        """
        self._rename_some_bad_file_name_patterns()

    @staticmethod
    def reformat_date_in_directory(directory: str) -> str:
        """
        Given a string that might represent a date based on the above regex, return
        a consistently formatted date string `YYYY_MM_DD`
        """
        re_date = re.match(BAD_DATE_REGEX_1, directory)
        if not re_date:
            # Not feeling great about this logic
            re_date = re.match(BAD_DATE_REGEX_2, directory)

        if not re_date:
            # Only reformat dates if they match the expected pattern.
            # Do nothing otherwise
            return directory

        month, day, year = re_date.groups()

        if len(year) == 2:
            # Assumes we only process dates from the year 2000 on
            year = "20" + year
        month = month.zfill(2)
        day = day.zfill(2)

        return f"{year}_{month}_{day}"

    def _are_data_files_named_correctly(self) -> None:
        """
        Crawls the entire data root directory and checks file names. No
        corrections are made here (yet)
        """
        builtin_print("")
        print("Checking data file names for consistency!")

        data_files = set()
        close_data_files = set()
        for root, _, files in os.walk(self.data_root):
          for file_name in files:
                if not file_name.endswith(".json"):
                    # Only walk for JSON files
                    continue
                if not re.search(DATETIME_REGEX, file_name):
                    # JSON files contain a specific date-time blob
                    continue
                if (
                    file_name.endswith("_processed.json")
                    or file_name.endswith("_analyzed.json")
                ):
                    # Other types of analysis process the data a certain way.
                    # This analysis may, too, but for now skip these.
                    continue

                file_name_parts = re.split(DATETIME_REGEX, file_name)
                exp_mouse_pairs = extract_exp_mouse_pairs(file_name_parts[0])
                if (
                    not exp_mouse_pairs
                    or any("-" in mouse_id for mouse_id in exp_mouse_pairs)
                ):
                    # Some JSON files are named incorrectly, or they contain
                    # the correct date-time string but no information on the
                    # experiment or mouse
                    close_data_files.add(os.path.join(root, file_name))
                    continue

                # These should be good.
                # But, check them!
                data_files.add(os.path.join(root, file_name))

        # Print a wrap-up of the output
        if data_files:
            print("Correctly named data files:")
            for f in data_files:
                builtin_print(f"  {f}")
        if close_data_files:
            print("Potential data files, incorrectly named:")
            for f in close_data_files:
                builtin_print(f"  {f}")
        else:
            print("No potential bad data files found!")

    def _rename_some_bad_file_name_patterns(self) -> None:
        builtin_print("")
        print("Renaming some incorrectly named files!")

        count_found = 0
        count_fixed = 0
        dry_run = True
        for root, _, files in os.walk(self.data_root):
            for file_name in files:
                if not file_name.endswith(".json"):
                    # Only walk for JSON files
                    continue
                if not re.search(DATETIME_REGEX, file_name):
                    # JSON files contain a specific date-time blob
                    continue

                file_name_parts = re.split(DATETIME_REGEX, file_name)
                exp_mouse_blob = file_name_parts[0]
                exp_mouse_pairs = extract_exp_mouse_pairs(exp_mouse_blob)
                if (
                    exp_mouse_pairs
                    and all("-" not in mouse_id for mouse_id in exp_mouse_pairs)
                ):
                    # This is a good file name. Skip it
                    continue
                count_found += 1

                bad_file = os.path.join(root, file_name)
                better_file = ""

                # Remove the `mouse_` prefix from some files
                prefix = "mouse_"
                if file_name.startswith(prefix):
                    better_file = os.path.join(root, file_name.split(prefix)[-1])

                # The `exp_mouse_blob` may accidentally have a `-` instead of `_`
                bad_char = "-"
                if bad_char in exp_mouse_blob:
                    rest_of_name = file_name.split(exp_mouse_blob)[-1]
                    exp_mouse_blob = exp_mouse_blob.replace("-", "_")
                    better_file_name = exp_mouse_blob + rest_of_name
                    better_file = os.path.join(root, better_file_name)

                # Continue if we did not find a way to define a better file
                if not better_file:
                    continue
                count_fixed += 1

                if dry_run:
                    print("Bad file found.")
                    builtin_print("  Would rename:")
                    builtin_print(f"    {bad_file}")
                    builtin_print("  To:")
                    builtin_print(f"    {better_file}")
                else:
                    os.rename(bad_file, better_file)

        if not count_found:
            print("Found no bad file names!")
        elif count_found == count_fixed:
            print("Fixed every bad file name we found!")
        else:
            print(f"Found {count_found} bad file names, fixed {count_fixed}!")

    def _rename_date_directories(self) -> None:
        """
        Method to rename the dates in data directories to be consistent
        """
        builtin_print("")
        print("Renaming some incorrectly named directories!")

        count = 0
        for root, directories, _ in os.walk(self.data_root):
            for directory in directories:
                bad_dir_match_1 = re.match(BAD_DATE_REGEX_1, directory)
                bad_dir_match_2 = re.match(BAD_DATE_REGEX_2, directory)

                need_to_fix_dir_name = False
                if bad_dir_match_1:
                    # We have a date like `3 25 24` or `3/25/24`
                    need_to_fix_dir_name = True
                elif bad_dir_match_2:
                    # We have a date like `3_25_24`
                    need_to_fix_dir_name = True

                if not need_to_fix_dir_name:
                    continue
                count += 1

                bad_path = os.path.join(root, directory)
                better_path = os.path.join(root, self.reformat_date_in_directory(directory))
                if self.dry_run:
                    print("Bad directory found.")
                    builtin_print("  Would rename:")
                    builtin_print(f"    {bad_path}")
                    builtin_print("  To:")
                    builtin_print(f"    {better_path}")
                else:
                    os.rename(bad_path, better_path)

        if not count:
            print("Found no bad directory names!")