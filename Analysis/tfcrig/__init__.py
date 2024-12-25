import re
from typing import Optional
from datetime import datetime
from tfcrig.files import DATETIME_REGEX


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
    exp_mouse_pairs = extract_exp_mouse_pairs(file_name_parts[0])
    # The magic `[0:-1]` removes a trailing underscore. Later raw data files
    # will be examined for mouse IDs that match their names
    return [e[0:-1] for e in exp_mouse_pairs]


def get_mouse_ids(file_paths: list[tuple[str,str,str]]) -> set[Optional[str]]:
    """
    Given the path to the root of the data directory, return a set of mouse
    IDs. Also checks that mouse ID, session ID pairs are unique
    """
    all_mouse_ids = []
    mouse_session_pairs = set()
    for _, _, files in file_paths:
        for file_name in files:
            if not is_data_file(file_name):
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


def is_data_file(file_name: str) -> bool:
    # Data files contain a specific date-time blob
    if not re.search(DATETIME_REGEX, file_name):
        return False

    # Data files have the format:
    #
    #     {exp_mouse_blob}_{datetime}.json
    #
    file_name_parts = re.split(DATETIME_REGEX, file_name)
    if file_name_parts[-1] != ".json":
        return False

    return True


def get_datetime_from_file_path(file_path: str) -> datetime:
    date_match = re.search(DATETIME_REGEX, file_path)
    if date_match:
        return datetime.strptime(date_match.group(), "%Y-%m-%d_%H-%M-%S")
    return None


def datetime_to_session_id(date_time: datetime) -> int:
    return int(date_time.strftime("%Y%m%d%H%M%S"))
