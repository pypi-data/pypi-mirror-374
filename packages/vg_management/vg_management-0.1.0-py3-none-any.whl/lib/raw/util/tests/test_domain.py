import pytest
from raw.util.domain import valid_domain


@pytest.mark.parametrize('case', [
    ("abc", False, "at least two components"),
    (
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        False,
        "maximum length is 253"
    ),
    ("abc%$#@()&^%;':.xyz.abc", False, "Domain component invalid"),
    ("abc123.com", True, None),
    (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        "aaaaaaaaaaaaaaaaaaaaaaa.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        True,
        None
     ),
    ("", False, "at least two components"),
    ("ab.cd.ef.gh", True, None),
    (".", False, "Domain component invalid"),
    ("a..b", False, "Domain component invalid"),
    ("a.", False, "Domain component invalid"),
    (".a", False, "Domain component invalid"),
    (
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        False,
        "Domain component invalid"
    ),
    (None, False, "not a str")
])
def test_valid_domain(case):

    domain_valid, domain_errlist = valid_domain(case[0])

    assert domain_valid == case[1]
    assert (case[2] is None) or (case[2] in domain_errlist[0])
