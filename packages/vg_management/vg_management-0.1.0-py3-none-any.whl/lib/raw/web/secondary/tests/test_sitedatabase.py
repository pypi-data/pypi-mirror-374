import pytest
from datetime import datetime
import sqlite3

from raw.web.secondary.database import SiteDatabase
from raw.util.database import Database


@pytest.fixture(scope="module")
def database_file(tmpdir_factory):

    tmpdir = tmpdir_factory.mktemp("test_sitedatabase")

    result = f"{tmpdir}/sitedatabase.db"

    return result


@pytest.fixture(scope="module")
def sdb(database_file):

    db = SiteDatabase(database_file, True)

    yield db

    db.close()
    db.delete_file()


def test_sitedb_instantiate_success(tmpdir):

    db = SiteDatabase(f"{tmpdir}/sdb1.db", True)

    assert isinstance(db, SiteDatabase)

    db.close()
    db.delete_file()


def test_sitedb_instantiate_fail_nocreate(tmpdir):

    with pytest.raises(ValueError):
        SiteDatabase(f"{tmpdir}/sdb1a.db", False)


# noinspection PyTypeChecker
def test_sitedb_instantiate_fail_badfilename(tmpdir):

    with pytest.raises(TypeError):
        SiteDatabase(47, True)


def test_sitedb_database(tmpdir):

    db = SiteDatabase(f"{tmpdir}/sdb2.db", True)

    assert isinstance(db.database, Database)

    db.close()
    db.delete_file()


def test_sitedb_connection(tmpdir):

    db = SiteDatabase(f"{tmpdir}/sdb3.db", True)

    assert isinstance(db.database.connection, sqlite3.Connection)

    db.close()
    db.delete_file()


def test_sitedb_filename(tmpdir):

    fn = f"{tmpdir}/sdb4.db"

    db = SiteDatabase(fn, True)

    assert db.filename == fn

    db.close()
    db.delete_file()


@pytest.mark.parametrize('case', [
    (
        "servers",
        [
            (0, "server_name", "", 1, None, 1),
            (1, "last_sync_attempt_time", "", 0, None, 0),
            (2, "last_sync_success_time", "", 0, None, 0),
            (3, "last_sync_ok", "", 0, None, 0),
            (4, "last_sync_err", "", 0, None, 0),
            (5, "ssh_port", "", 0, None, 0),
            (6, "ssh_user", "", 0, None, 0),
        ]
    ),
    (
        "users",
        [
            (0, "user_name", "", 1, None, 1),
            (1, "master_server", "", 1, None, 0),
            (2, "last_sync_attempt_time", "", 0, None, 0),
            (3, "last_sync_success_time", "", 0, None, 0),
            (4, "last_sync_ok", "", 0, None, 0),
            (5, "last_sync_err", "", 0, None, 0),
            (6, "ssh_port", "", 0, None, 0),
            (7, "ssh_user", "", 0, None, 0),
            (8, "implicit", "", 1, None, 0)
        ],
    ),
])
def test_database_creation_correct_schema(sdb, case):

    rows = sdb.database.get_db_table_schema(case[0])

    assert rows == case[1]


@pytest.mark.parametrize('case', [
    {
        "server_name":              "mercury",
        "last_sync_attempt_time":   datetime(2016, 11, 27, 14, 42, 5),
        "last_sync_success_time":   datetime(2016, 11, 27, 12, 11, 21),
        "last_sync_ok":             False,
        "last_sync_err":            "Didn't work",
        "ssh_port":                 22614,
        "ssh_user":                 "root",
    },
    {
        "server_name":              "venus",
        "last_sync_attempt_time":   datetime(2016, 4, 15, 21, 37, 28),
        "last_sync_success_time":   datetime(2016, 4, 15, 21, 37, 28),
        "last_sync_ok":             True,
        "last_sync_err":            None,
        "ssh_port":                 22614,
        "ssh_user":                 "root",
    },
    {
        "server_name":              "earth",
        "last_sync_attempt_time":   datetime(2017, 5, 30, 2, 52, 11),
        "last_sync_success_time":   None,
        "last_sync_ok":             False,
        "last_sync_err":            "Didn't work",
        "ssh_port":                 22614,
        "ssh_user":                 "root",
    },
    {
        "server_name":              "mars",
        "last_sync_attempt_time":   None,
        "last_sync_success_time":   None,
        "last_sync_ok":             False,
        "last_sync_err":            None,
        "ssh_port":                 22,
        "ssh_user":                 "root",
    },
    {
        "server_name":              "jupiter",
        "last_sync_attempt_time":   datetime(2018, 7, 13, 0, 3, 33),
        "last_sync_success_time":   datetime(2018, 7, 13, 0, 3, 33),
        "last_sync_ok":             True,
        "last_sync_err":            None,
        "ssh_port":                 22,
        "ssh_user":                 "brian",
    },
    {
        "server_name":              "saturn",
        "last_sync_attempt_time":   datetime(2020, 11, 27, 14, 42, 5),
        "last_sync_success_time":   datetime(2020, 11, 27, 12, 11, 21),
        "last_sync_ok":             False,
        "last_sync_err":            "Didn't work",
        "ssh_port":                 22614,
        "ssh_user":                 "root",
    },
])
def test_sitedb_insert_servers(sdb, case):

    sdb.create_server(**case)

    conn = sqlite3.connect(sdb.filename)

    cur = conn.cursor()

    cur.execute("select * from servers where server_name=?", (case["server_name"],))

    rows = cur.fetchall()

    assert rows == [
        (
            sdb.database.convert_col_to_db(case["server_name"], "servers", "server_name"),
            sdb.database.convert_col_to_db(case["last_sync_attempt_time"], "servers", "last_sync_attempt_time"),
            sdb.database.convert_col_to_db(case["last_sync_success_time"], "servers", "last_sync_success_time"),
            sdb.database.convert_col_to_db(case["last_sync_ok"], "servers", "last_sync_ok"),
            sdb.database.convert_col_to_db(case["last_sync_err"], "servers", "last_sync_err"),
            sdb.database.convert_col_to_db(case["ssh_port"], "servers", "ssh_port"),
            sdb.database.convert_col_to_db(case["ssh_user"], "servers", "ssh_user"),
        )
    ]

    cur.close()
    conn.close()


@pytest.mark.parametrize('case', [
    (
        {
            "server_name":              "mercury",
            "last_sync_attempt_time":   datetime(2016, 11, 27, 14, 42, 5),
            "last_sync_success_time":   datetime(2016, 11, 27, 12, 11, 21),
            "last_sync_ok":             False,
            "last_sync_err":            "Didn't work",
            "ssh_port":                 22614,
            "ssh_user":                 "root",
        },
        sqlite3.IntegrityError,
    ),
    (
        {
            "server_name":              None,
        },
        ValueError,
    ),
    (
        {
            "server_name":              "xyz123",
            "last_sync_attempt_time":   47,
        },
        TypeError,
    ),
    (
        {
            "server_name":                  "abc456",
            "last_sync_attempt_time":       datetime(2016, 4, 15, 21, 37, 28),
            "last_sync_success_time":       datetime(2016, 4, 15, 21, 37, 28),
            "last_sync_ok":                 3,
        },
        TypeError,
    ),
])
def test_sitedb_insert_servers_fail(sdb, case):

    with pytest.raises(case[1]):
        sdb.create_server(**dict(case[0]))

    sdb.database.connection.rollback()



@pytest.mark.parametrize('case', [
    (
        {
            "server_name":                  "mercury",
        },
        [
            {
                "server_name":              "mercury",
                "last_sync_attempt_time":   datetime(2016, 11, 27, 14, 42, 5),
                "last_sync_success_time":   datetime(2016, 11, 27, 12, 11, 21),
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            }
        ]
    ),
    (
        {
            "server_name":                  "venus",
        },
        [
            {
                "server_name":              "venus",
                "last_sync_attempt_time":   datetime(2016, 4, 15, 21, 37, 28),
                "last_sync_success_time":   datetime(2016, 4, 15, 21, 37, 28),
                "last_sync_ok":             True,
                "last_sync_err":            None,
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            }
        ]
    ),
    (
        {
            "server_name":                  "earth",
        },
        [
            {
                "server_name":              "earth",
                "last_sync_attempt_time":   datetime(2017, 5, 30, 2, 52, 11),
                "last_sync_success_time":   None,
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            }
        ]
    ),
    (
        {
            "server_name":                  "mars",
        },
        [
            {
                "server_name":              "mars",
                "last_sync_attempt_time":   None,
                "last_sync_success_time":   None,
                "last_sync_ok":             False,
                "last_sync_err":            None,
                "ssh_port":                 22,
                "ssh_user":                 "root",
            }
        ]
    ),
    (
        {
            "server_name":                  "jupiter",
        },
        [
            {
                "server_name":              "jupiter",
                "last_sync_attempt_time":   datetime(2018, 7, 13, 0, 3, 33),
                "last_sync_success_time":   datetime(2018, 7, 13, 0, 3, 33),
                "last_sync_ok":             True,
                "last_sync_err":            None,
                "ssh_port":                 22,
                "ssh_user":                 "brian",
            }
        ]
    ),
    (
        {
            "server_name":                  "saturn",
        },
        [
            {
                "server_name":              "saturn",
                "last_sync_attempt_time":   datetime(2020, 11, 27, 14, 42, 5),
                "last_sync_success_time":   datetime(2020, 11, 27, 12, 11, 21),
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            }
        ]
    ),
    (
        {
            "last_sync_err":                "Didn't work",
        },
        [
            {
                "server_name": "mercury",
                "last_sync_attempt_time":   datetime(2016, 11, 27, 14, 42, 5),
                "last_sync_success_time":   datetime(2016, 11, 27, 12, 11, 21),
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            },
            {
                "server_name":              "earth",
                "last_sync_attempt_time":   datetime(2017, 5, 30, 2, 52, 11),
                "last_sync_success_time":   None,
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            },
            {
                "server_name":              "saturn",
                "last_sync_attempt_time":   datetime(2020, 11, 27, 14, 42, 5),
                "last_sync_success_time":   datetime(2020, 11, 27, 12, 11, 21),
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            },
        ]
    ),
    (
        {
            "ssh_port":                     22,
            "last_sync_err":                None,
        },
        [
            {
                "server_name":              "mars",
                "last_sync_attempt_time":   None,
                "last_sync_success_time":   None,
                "last_sync_ok":             False,
                "last_sync_err":            None,
                "ssh_port":                 22,
                "ssh_user":                 "root",
            },
            {
                "server_name":              "jupiter",
                "last_sync_attempt_time":   datetime(2018, 7, 13, 0, 3, 33),
                "last_sync_success_time":   datetime(2018, 7, 13, 0, 3, 33),
                "last_sync_ok":             True,
                "last_sync_err":            None,
                "ssh_port":                 22,
                "ssh_user":                 "brian",
            },
        ]
    ),
    (
        {
            "server_name":                  "mercury",
            "last_sync_attempt_time":       datetime(2016, 11, 27, 14, 42, 5),
            "last_sync_success_time":       datetime(2016, 11, 27, 12, 11, 21),
            "last_sync_ok":                 False,
            "last_sync_err":                "Didn't work",
            "ssh_port":                     22614,
            "ssh_user":                     "root",
        },
        [
            {
                "server_name":              "mercury",
                "last_sync_attempt_time":   datetime(2016, 11, 27, 14, 42, 5),
                "last_sync_success_time":   datetime(2016, 11, 27, 12, 11, 21),
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22614,
                "ssh_user":                 "root",
            },
        ]
    ),
    (
        {
            "ssh_port":                     997,
        },
        [
        ]
    )
])
def test_sitedb_get_servers(sdb, case):

    # noinspection PyTypeChecker
    server_list = sdb.get_servers(**dict(case[0]))

    server_list_asdict = list(map(lambda s: s.asdict(), server_list))

    # noinspection PyTypeChecker
    assert server_list_asdict == list(case[1])


@pytest.mark.parametrize('case', [
    (
        None,
        TypeError
    ),
    (
        {
            "banana":           77,
        },
        KeyError
    ),
    (
        {
            "ssh_port":         "blarg",
        },
        TypeError
    )
])
def test_sitedb_get_servers_fail(sdb, case):

    with pytest.raises(case[1]):
        sdb.get_servers(**dict(case[0]))


@pytest.mark.parametrize('case', [
    (
        {
            "server_name":          "venus",
        },
        {
            "ssh_user":             "sys"
        }
    ),
    (
        {
            "server_name":          "earth",
        },
        {
            "ssh_user":             "web",
            "ssh_port":             999,
        }
    ),
])
def test_sitedb_update_servers(sdb, case):

    server_list = sdb.get_servers(**dict(case[0]))

    assert len(server_list) == 1

    server = server_list[0]

    for k in dict(case[1]).keys():

        setattr(server, k, dict(case[1])[k])

    server.update()

    server_list2 = sdb.get_servers(**dict(case[0]))

    assert len(server_list2) == 1

    server2 = server_list2[0]

    for k in dict(case[1]).keys():

        assert getattr(server2, k) == dict(case[1])[k]


@pytest.mark.parametrize('case', [
    {
        "server_name":                  "earth"
    },
    {
        "server_name":                  "mars"
    },
])
def test_sitedb_delete_servers(sdb, case):

    server_list = sdb.get_servers(**case)

    assert len(server_list) == 1

    server = server_list[0]

    server.delete()

    server_list2 = sdb.get_servers(**case)

    assert len(server_list2) == 0


@pytest.mark.parametrize('case', [
    {
        "user_name":                "alice",
        "master_server":            "venus",
        "last_sync_attempt_time":   datetime(2017, 2, 7, 4, 11, 5),
        "last_sync_success_time":   datetime(2017, 2, 3, 12, 11, 21),
        "last_sync_ok":             False,
        "last_sync_err":            "Broken",
        "ssh_port":                 22614,
        "ssh_user":                 "alice",
        "implicit":                 True,
    },
    {
        "user_name":                "bob",
        "master_server":            "venus",
        "last_sync_attempt_time":   datetime(2016, 4, 15, 21, 37, 28),
        "last_sync_success_time":   datetime(2016, 4, 15, 21, 37, 28),
        "last_sync_ok":             True,
        "last_sync_err":            None,
        "ssh_port":                 22614,
        "ssh_user":                 "bob",
        "implicit":                 True,
    },
    {
        "user_name":                "charlie",
        "master_server":            "earth",
        "last_sync_attempt_time":   datetime(2017, 5, 30, 2, 52, 11),
        "last_sync_success_time":   None,
        "last_sync_ok":             False,
        "last_sync_err":            "Didn't work",
        "ssh_port":                 22,
        "ssh_user":                 "root",
        "implicit":                 False,
    },
])
def test_sitedb_insert_users(sdb, case):

    new_server = sdb.create_user(**case)

    conn = sqlite3.connect(sdb.filename)

    cur = conn.cursor()

    cur.execute("select * from users where user_name=?", (case["user_name"],))

    rows = cur.fetchall()

    assert rows == [
        (
            sdb.database.convert_col_to_db(case["user_name"], "users", "user_name"),
            sdb.database.convert_col_to_db(case["master_server"], "users", "master_server"),
            sdb.database.convert_col_to_db(case["last_sync_attempt_time"], "users", "last_sync_attempt_time"),
            sdb.database.convert_col_to_db(case["last_sync_success_time"], "users", "last_sync_success_time"),
            sdb.database.convert_col_to_db(case["last_sync_ok"], "users", "last_sync_ok"),
            sdb.database.convert_col_to_db(case["last_sync_err"], "users", "last_sync_err"),
            sdb.database.convert_col_to_db(case["ssh_port"], "users", "ssh_port"),
            sdb.database.convert_col_to_db(case["ssh_user"], "users", "ssh_user"),
            sdb.database.convert_col_to_db(case["implicit"], "users", "implicit"),
        )
    ]

    cur.close()
    conn.close()


@pytest.mark.parametrize('case', [
    (
        {
            "user_name":                "alice",
            "master_server":            "venus",
            "last_sync_attempt_time":   datetime(2017, 2, 7, 4, 11, 5),
            "last_sync_success_time":   datetime(2017, 2, 3, 12, 11, 21),
            "last_sync_ok":             False,
            "last_sync_err":            "Broken",
            "ssh_port":                 22614,
            "ssh_user":                 "alice",
            "implicit":                 True,
        },
        sqlite3.IntegrityError,
    ),
    (
        {
            "user_name":                "sharon",
            "master_server":            "venus",
            "last_sync_attempt_time":   datetime(2017, 2, 7, 4, 11, 5),
            "last_sync_success_time":   datetime(2017, 2, 3, 12, 11, 21),
            "last_sync_ok":             False,
            "last_sync_err":            "Broken",
            "ssh_port":                 22614,
            "ssh_user":                 "alice",
        },
        ValueError,
    ),
    (
        {
            "user_name":                None,
            "master_server":            "jupiter",
            "implicit":                 False,
        },
        ValueError,
    ),
    (
        {
            "user_name":                "xyz123",
            "master_server":            "venus",
            "last_sync_attempt_time":   47,
            "implicit":                 False,
        },
        TypeError,
    ),
    (
        {
            "user_name":                    "abc456",
            "master_server":                "mars",
            "last_sync_attempt_time":       datetime(2016, 4, 15, 21, 37, 28),
            "last_sync_success_time":       datetime(2016, 4, 15, 21, 37, 28),
            "last_sync_ok":                 3,
            "implicit":                     False,
        },
        TypeError,
    ),
])
def test_sitedb_insert_users_fail(sdb, case):

    with pytest.raises(case[1]):
        new_user = sdb.create_user(**case[0])

    sdb.database.connection.rollback()


@pytest.mark.parametrize('case', [
    (
        {
            "user_name":                    "alice",
        },
        [
            {
                "user_name":                "alice",
                "master_server":            "venus",
                "last_sync_attempt_time":   datetime(2017, 2, 7, 4, 11, 5),
                "last_sync_success_time":   datetime(2017, 2, 3, 12, 11, 21),
                "last_sync_ok":             False,
                "last_sync_err":            "Broken",
                "ssh_port":                 22614,
                "ssh_user":                 "alice",
                "implicit":                 True,
            },
        ]
    ),
    (
        {
            "user_name":                    "bob",
        },
        [
            {
                "user_name":                "bob",
                "master_server":            "venus",
                "last_sync_attempt_time":   datetime(2016, 4, 15, 21, 37, 28),
                "last_sync_success_time":   datetime(2016, 4, 15, 21, 37, 28),
                "last_sync_ok":             True,
                "last_sync_err":            None,
                "ssh_port":                 22614,
                "ssh_user":                 "bob",
                "implicit":                 True,
            },
        ]
    ),
    (
        {
            "user_name":                    "charlie",
        },
        [
            {
                "user_name":                "charlie",
                "master_server":            "earth",
                "last_sync_attempt_time":   datetime(2017, 5, 30, 2, 52, 11),
                "last_sync_success_time":   None,
                "last_sync_ok":             False,
                "last_sync_err":            "Didn't work",
                "ssh_port":                 22,
                "ssh_user":                 "root",
                "implicit":                 False,
            },
        ]
    ),
    (
        {
            "ssh_port":                     22614,
        },
        [
            {
                "user_name":                "alice",
                "master_server":            "venus",
                "last_sync_attempt_time":   datetime(2017, 2, 7, 4, 11, 5),
                "last_sync_success_time":   datetime(2017, 2, 3, 12, 11, 21),
                "last_sync_ok":             False,
                "last_sync_err":            "Broken",
                "ssh_port":                 22614,
                "ssh_user":                 "alice",
                "implicit":                 True,
            },
            {
                "user_name":                "bob",
                "master_server":            "venus",
                "last_sync_attempt_time":   datetime(2016, 4, 15, 21, 37, 28),
                "last_sync_success_time":   datetime(2016, 4, 15, 21, 37, 28),
                "last_sync_ok":             True,
                "last_sync_err":            None,
                "ssh_port":                 22614,
                "ssh_user":                 "bob",
                "implicit":                 True,
            },
        ]
    ),
])
def test_sitedb_get_users(sdb, case):

    user_list = sdb.get_users(**case[0])

    user_list_asdict = list(map(lambda u: u.asdict(), user_list))

    assert user_list_asdict == case[1]


@pytest.mark.parametrize('case', [
    (
        None,
        TypeError
    ),
    (
        {
            "banana":                       45,
        },
        KeyError
    ),
    (
        {
            "ssh_port":                     "x",
        },
        TypeError
    )
])
def test_sitedb_get_users_fail(sdb, case):

    with pytest.raises(case[1]):
        result = sdb.get_users(**case[0])


@pytest.mark.parametrize('case', [
    (
        {
            "user_name":            "alice",
        },
        {
            "master_server":        "earth"
        }
    ),
    (
        {
            "user_name":            "bob",
        },
        {
            "ssh_user":             "snarf",
            "ssh_port":             42,
        }
    ),
])
def test_sitedb_update_users(sdb, case):

    user_list = sdb.get_users(**case[0])

    assert len(user_list) == 1

    user = user_list[0]

    for k in case[1].keys():

        setattr(user, k, case[1][k])

    user.update()

    user_list2 = sdb.get_users(**case[0])

    assert len(user_list2) == 1

    user2 = user_list2[0]

    for k in case[1].keys():

        assert getattr(user2, k) == case[1][k]


@pytest.mark.parametrize('case', [
    {
        "user_name":                    "alice"
    },
    {
        "user_name":                    "bob"
    },
])
def test_sitedb_delete_users(sdb, case):

    user_list = sdb.get_users(**case)

    assert len(user_list) == 1

    user = user_list[0]

    user.delete()

    user_list2 = sdb.get_users(**case)

    assert len(user_list2) == 0
