import pytest
from raw.util.ip import is_martian_ip


@pytest.mark.parametrize('case', [
    ("10.0.0.1", True),
    ("10.223.254.254", True),
    ("172.15.22.4", False),
    ("172.16.1.1", True),
    ("172.21.4.22", True),
    ("172.24.54.222", False),
    ("192.167.1.1", False),
    ("192.168.1.1", True),
    ("192.168.255.255", True),
    ("192.169.1.1", False),
    ("0.0.0.0", True),
    ("0.255.255.255", True),
    ("255.255.255.255", True),
    ("255.0.1.2", True),
    ("127.0.0.1", True),
    ("127.255.255.255", True),
    ("224.1.1.1", True),
    ("1.1.1.1", False),
    ("8.8.8.8", False),
    ("132.181.27.3", False),
    ("202.20.93.10", False)
])
def test_martian(case):

    result = is_martian_ip(case[0])

    assert result == case[1]
