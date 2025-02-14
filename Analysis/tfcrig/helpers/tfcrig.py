"""
Helper functions with custom, tFC-rig-specific logic
"""
import re
from typing import Optional
from datetime import datetime

DATETIME_REGEX = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}"
"""
Regex matching for a datetime of the format `YYYY-MM-DD_HH-MM-SS` which
is included in the file names generated during data collection
"""

FILENAME_REGEX = DATETIME_REGEX + r".json"
"""
Base data files end in the datetime and are of type JSON
"""


def create_cohort_pattern(root_path: str) -> re.Pattern:
    """
    Return a regex pattern that starts with the given root path, followed by a
    cohort folder, then followed by anything. This assumes that cohorts can use
    any roman numeral, but that they start with one. It assumes that cohort
    data folders are at the top-level of the root path
    """
    if root_path.endswith("/"):
        escaped_root = re.escape(root_path[:-1])
    else:
        escaped_root = re.escape(root_path)

    # The `cohort_pattern` is any roman numeral, in this case up to 39 (XXXIX),
    # although over time more than 39 cohorts may exist and this will need to
    # be updated
    cohort_pattern = r'(?P<cohort>[IVX]{1,7})'

    # Complete pattern:
    # - Start with escaped root path
    # - Followed by /
    # - Then the cohort
    # - Followed by an underscore and any character
    # - Then / and any remaining path
    pattern = fr'{escaped_root}/{cohort_pattern}_[^/]*(?:/.*)?$'

    return re.compile(pattern)


def extract_cohort(path: str, pattern: re.Pattern) -> str:
    """
    Extracts the IVX sequence from a matching path.
    Returns None if path doesn't match the pattern.
    """
    re_match = pattern.match(path)
    if re_match:
        return re_match.group("cohort")
    return None


def extract_cohort_mouse_pairs(cohort_mouse_blob: str) -> list[str]:
    """
    Define a recursive function that helps extract sets of
    `{cohort_id}_{mouse_id}_` from a file name. It accepts the
    front portion of a session file name and returns a list of
    these sets
    """
    if not isinstance(cohort_mouse_blob, str):
        raise TypeError(
            f"Can only search strings for cohort, mouse pairs!"
        )

    if not cohort_mouse_blob:
        raise ValueError(
            f"Can only search non-empty strings for cohort, mouse pairs!"
        )

    date_match = re.search(DATETIME_REGEX, cohort_mouse_blob)
    if date_match:
        raise ValueError(
            f"Provided string '{cohort_mouse_blob}' still contains a date-time!"
        )

    pattern = r"\d+[_-]\d+[_-]"
    string_match = re.search(pattern, cohort_mouse_blob)

    if string_match:
        first_pair = string_match.group()
        rest_of_string = cohort_mouse_blob[string_match.end() :]
        if rest_of_string:
            return [first_pair] + extract_cohort_mouse_pairs(rest_of_string)
        return [first_pair]
    raise ValueError(
        f"Provided string or sub-string '{cohort_mouse_blob}' does not "
        "contain a cohort, mouse pair!"
    )


def root_contains_cohort_of_interest(
    root: str,
    cohort_pattern: re.Pattern,
    cohorts: Optional[list[str]],
) -> bool:
    """
    Used to check whether the given root path is worth examining based on
    the input list of `cohorts` if provided
    """
    cohort = extract_cohort(root, cohort_pattern)

    # If no cohort is found, we aren't working with cohort data!
    if not cohort:
        return False

    # It is always a cohort of interest if no cohorts are provided
    if not cohorts:
        return True

    # Otherwise only return `True` for cohorts-of-interest
    if cohort in cohorts:
        return True

    return False


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
        rest_of_string = exp_mouse_blob[string_match.end() :]
        return [first_pair] + extract_exp_mouse_pairs(rest_of_string)
    return []


def get_mouse_ids_from_file_name(file_name: str) -> list[Optional[str]]:
    file_name_parts = re.split(DATETIME_REGEX, file_name)
    exp_mouse_pairs = extract_cohort_mouse_pairs(file_name_parts[0])
    # The magic `[0:-1]` removes a trailing underscore. Later raw data files
    # will be examined for mouse IDs that match their names
    return [e[0:-1] for e in exp_mouse_pairs]


def get_mouse_ids(os_walk: list[tuple[str,str,str]]) -> set[Optional[str]]:
    """
    Given the path to the root of the data directory, return a set of mouse
    IDs. Also checks that mouse ID, session ID pairs are unique
    """
    all_mouse_ids = []
    mouse_session_pairs = set()
    for _, _, files in os_walk:
        for file_name in files:
            if not is_base_data_file(file_name):
                continue

            mouse_ids = get_mouse_ids_from_file_name(file_name)
            session_id = datetime_to_session_id(get_datetime_from_file_path(file_name))

            # Mouse ID, session ID pairs should be unique
            for mouse_id in mouse_ids:
                key = (mouse_id, session_id)
                if key in mouse_session_pairs:
                    raise ValueError(
                        "Found non-unique mouse id, session id pair: "
                        f"({mouse_id}, {session_id})"
                    )
                mouse_session_pairs.add(key)
            all_mouse_ids += mouse_ids

    return set(mouse_ids)


def is_base_data_file(file_name: str) -> bool:
    """
    Given a file name, determine whether it is an base data file.
    These are JSON files used to build the data frame for the analysis.
    They are not the raw, analyzed, or processed data that may be used
    as an intermediate step in the analysis
    """
    if re.search(FILENAME_REGEX, file_name):
        return True
    return False


def get_datetime_from_file_path(file_path: str) -> datetime:
    date_match = re.search(DATETIME_REGEX, file_path)
    if date_match:
        return datetime.strptime(date_match.group(), "%Y-%m-%d_%H-%M-%S")
    return None


def datetime_to_session_id(date_time: datetime) -> int:
    return int(date_time.strftime("%Y%m%d%H%M%S"))
