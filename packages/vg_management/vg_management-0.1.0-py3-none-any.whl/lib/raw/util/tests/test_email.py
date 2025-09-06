import pytest
from raw.util.email import valid_email


@pytest.mark.parametrize('case', [
    (None, False),
    ("", False),
    ("x", False),
    ("x.y", False),
    ("@", False),
    (".", False),
    ("a@b.c", True),
    ("a@b", False),
    ("a@b@c", False),
    ("user@domain.com", True),
    ("user@subdomain.domain.com", True),
    ("user+ref@domain.com", True),
    ("user-ref@domain.com", True),
    ("SOMEONE@SOMEWHERE.COM", True)
])
def test_valid_email(case):

    valid = valid_email(case[0])

    assert valid == case[1]
