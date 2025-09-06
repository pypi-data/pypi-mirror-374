import pytest
import sys
import os
from lib.raw.web.config import WebConfiguration

sys.path.append(os.path.abspath(".."))

from libexec.new_user import check_domain, check_email, check_username, check_user_exists


@pytest.mark.parametrize('case', [
    "abc.com",
    "sub.abc.com",
    "1st.com",
    "xya.nz",
    "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    "xxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "its-ok.com",
    "still--ok.com",
    "i.like.sub.domains.org",
    "0123456789.net"
])
def test_check_domain(case):

    config = WebConfiguration()
    config.domain_name = case

    check_domain(config)

    assert True


@pytest.mark.parametrize('case', [
    ("", RuntimeError),
    (".", RuntimeError),
    (".com", RuntimeError),
    ("not_valid.com", RuntimeError),
    (
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.com",
        RuntimeError
    ),
    (
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx."
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx."
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx."
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx."
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx."
        "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        RuntimeError
    ),
    ("a$c.org", RuntimeError),
    ("-nope.com", RuntimeError),
    ("nope-.com", RuntimeError),
    ("nope.com-", RuntimeError),
    (1, RuntimeError),
    (None, RuntimeError)
])
def test_check_domain_fail(case):

    config = WebConfiguration()
    config.domain_name = case[0]

    with pytest.raises(case[1]):
        check_domain(config)


@pytest.mark.parametrize('case', [
    "a@c.com",
    "support@blarg.com",
    "me@yes.you.over.there.com",
    "hey@yes-you.com",
    "email+sub@snarf.gov",
    "bing-bong@microsoft.com",
    "coach@49ers.org",
    "abcdefghijklmnopqrstuvwxyz!#$%&‘*+/=?^_`.{|}~@ok.com",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@GOOD.NET",
    "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz@itsallgood.org"
])
def test_check_email(case):

    config = WebConfiguration()
    config.webmaster_email = case

    check_email(config)

    assert True


@pytest.mark.parametrize('case', [
    ("", RuntimeError),
    ("a", RuntimeError),
    ("@", RuntimeError),
    ("a@", RuntimeError),
    ("@x", RuntimeError),
    ("me@-invalid.com", RuntimeError),
    ("you@xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.com", RuntimeError),
    ("person@yes$you.com", RuntimeError),
    ("email@a.b.c.not_valid.com", RuntimeError),
    ("person@-wrong.net", RuntimeError),
    ("someone@broken-.com", RuntimeError),
    ("abc@def@ghi.com", RuntimeError),
    ("ab:cd@xyz.com", RuntimeError),
    ("toolong!toolong!toolong!toolong!toolong!toolong!toolong!toolong!x@long.gov", RuntimeError),
    (None, RuntimeError),
    (42, RuntimeError)
])
def test_check_email_fail(case):

    config = WebConfiguration()
    config.webmaster_email = case[0]

    with pytest.raises(case[1]):

        check_email(config)


@pytest.mark.parametrize('case', [
    "aa",
    "aaaaaaaaaaaa",
    "abcdefghijkl",
    "mnopqrstuvwx",
    "yz",
    "u0123456789"
])
def test_check_username(case):

    config = WebConfiguration()
    config.username = case

    check_username(config)

    assert True


@pytest.mark.parametrize('case', [
    ("", RuntimeError),
    ("a", RuntimeError),
    ("aaaaaaaaaaaaa", RuntimeError),
    ("1", RuntimeError),
    ("1a", RuntimeError),
    ("a^^$", RuntimeError),
    ("ab cd", RuntimeError)
])
def test_check_username_fail(case):

    config = WebConfiguration()
    config.username = case[0]

    with pytest.raises(case[1]):

        check_username(config)


@pytest.mark.parametrize('case', [
    "root",
    "bin",
    "daemon",
    "adm",
    "",
    "1invalidname",
    "#$%*&^&*"
])
def test_check_user_exists(case):

    config = WebConfiguration()
    config.username = case

    with pytest.raises(RuntimeError):

        check_user_exists(config)


@pytest.mark.parametrize('case', [
    "wibblesnarf",
])
def test_check_user_exists_fail(case):

    config = WebConfiguration()
    config.username = case

    check_user_exists(config)

    assert True
