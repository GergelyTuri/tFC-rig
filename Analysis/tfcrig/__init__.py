import re
from typing import Optional


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
    pattern: re.Pattern,
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
