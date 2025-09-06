import pytest
from raw.util.user import valid_username, user_account_exists, group_exists


@pytest.mark.parametrize('case', [
    ("", False, "must be between 2 and "),
    ("a", False, "must be between 2 and "),
    ("  ", False, "Username is invalid"),
    ("xx", True, None),
    ("abcdabcdabcd", True, None),
    ("1abc", False, "cannot start with a digit"),
    ("abcdabcdabcda", False, "must be between 2 and "),
    ("snarf", True, None),
    ("a^%4", False, "Username is invalid"),
    ("abc 123", False, "Username is invalid"),
    (None, False, "must be str"),
])
def test_valid_username(case):

    valid, errors = valid_username(case[0])

    assert valid == case[1]
    assert (case[2] is None) or (case[2] in errors[0])


@pytest.mark.parametrize('case', [
    ("root", True),
    ("yadayada", False)
])
def test_user_exists(case):

    result = user_account_exists(case[0])

    assert result == case[1]


@pytest.mark.parametrize('case', [
    ("root", True),
    ("yadayada", False)
])
def test_group_exists(case):

    result = group_exists(case[0])

    assert result == case[1]
