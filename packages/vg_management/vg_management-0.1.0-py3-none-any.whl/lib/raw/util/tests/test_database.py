import pytest
import os
from typing import Dict
import datetime
import sqlite3

from raw.util.database import Database, DatabaseField


database_schema: Dict[str, Dict[str, DatabaseField]] = {
    "servers": {
        "server_name":
            DatabaseField(
                columnname="server_name",
                dbtype=str,
                pythontype=str,
                primarykey=True,
                nullable=False
            ),
        "last_sync_attempt_time":
            DatabaseField(
                columnname="last_sync_attempt_time",
                dbtype=str,
                pythontype=datetime.datetime,
                primarykey=False,
                nullable=True
            ),
        "last_sync_success_time":
            DatabaseField(
                columnname="last_sync_attempt_time",
                dbtype=str,
                pythontype=datetime.datetime,
                primarykey=False,
                nullable=True
            ),
        "last_sync_ok":
            DatabaseField(
                columnname="last_sync_ok",
                dbtype=int,
                pythontype=bool,
                primarykey=False,
                nullable=True
            ),
        "last_sync_err":
            DatabaseField(
                columnname="last_sync_err",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True
            ),
        "ssh_port":
            DatabaseField(
                columnname="ssh_port",
                dbtype=int,
                pythontype=int,
                primarykey=False,
                nullable=True
            ),
        "ssh_user":
            DatabaseField(
                columnname="ssh_user",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True
            )
    },
    "users": {
        "user_name":
            DatabaseField(
                columnname="user_name",
                dbtype=str,
                pythontype=str,
                primarykey=True,
                nullable=False
            ),
        "master_server":
            DatabaseField(
                columnname="master_server",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=False
            ),
        "last_sync_attempt_time":
            DatabaseField(
                columnname="last_sync_attempt_time",
                dbtype=str,
                pythontype=datetime.datetime,
                primarykey=False,
                nullable=True
            ),
        "last_sync_success_time":
            DatabaseField(
                columnname="last_sync_attempt_time",
                dbtype=str,
                pythontype=datetime.datetime,
                primarykey=False,
                nullable=True
            ),
        "last_sync_ok":
            DatabaseField(
                columnname="last_sync_ok",
                dbtype=int,
                pythontype=bool,
                primarykey=False,
                nullable=True
            ),
        "last_sync_err":
            DatabaseField(
                columnname="last_sync_err",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True
            ),
        "ssh_port":
            DatabaseField(
                columnname="ssh_port",
                dbtype=int,
                pythontype=int,
                primarykey=False,
                nullable=True
            ),
        "ssh_user":
            DatabaseField(
                columnname="ssh_user",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True
            ),
        "implicit":
            DatabaseField(
                columnname="implicit",
                dbtype=int,
                pythontype=bool,
                primarykey=False,
                nullable=False
            )
    }
}


new_table_schema: Dict[str, DatabaseField] = dict({
    "pk":
        DatabaseField(
            columnname="pk",
            dbtype=int,
            pythontype=int,
            primarykey=True,
            nullable=False
        ),
    "blarg":
        DatabaseField(
            columnname="blarg",
            dbtype=str,
            pythontype=str,
            primarykey=False,
            nullable=True
        ),
    "snarf":
        DatabaseField(
            columnname="snarf",
            dbtype=int,
            pythontype=bool,
            primarykey=False,
            nullable=False
        )
})


@pytest.fixture(scope="module")
def database_file(tmpdir_factory):

    fn = Database.make_filename(tmpdir_factory.mktemp("sqlite3_database"))
    return fn


@pytest.fixture(scope="module")
def db(database_file):

    db = Database(database_file, database_schema, True)

    yield db

    db.close()
    db.delete_file()


def test_database_instantiate_success(tmpdir):

    fn = Database.make_filename(tmpdir)
    db = Database(fn, database_schema, True)

    assert isinstance(db, Database)


# noinspection PyArgumentList
def test_database_instantiate_typeerror():

    with pytest.raises(TypeError):
        Database()


def test_database_instantiate_valueerror(tmpdir):

    fn = Database.make_filename(tmpdir)
    with pytest.raises(TypeError):
        Database(fn)


def test_database_instantiate_no_create(tmpdir):

    fn = Database.make_filename(tmpdir)
    with pytest.raises(ValueError):
        Database(fn, database_schema, False)


def test_database_instantiate_empty_schema1(tmpdir):

    fn = Database.make_filename(tmpdir)
    with pytest.raises(ValueError):
        Database(fn, dict(), True)


def test_database_instantiate_empty_schema2(tmpdir):

    fn = Database.make_filename(tmpdir)
    with pytest.raises(ValueError):
        Database(fn, dict({"t1": {}}), True)


def test_database_filename(tmpdir):

    fn = Database.make_filename(tmpdir)
    db = Database(fn, database_schema, True)
    assert db.filename == fn


def test_database_schema(tmpdir):

    fn = Database.make_filename(tmpdir)
    db = Database(fn, database_schema, True)
    assert db.schema == database_schema


def test_database_connection(tmpdir):

    fn = Database.make_filename(tmpdir)
    db = Database(fn, database_schema, True)
    assert isinstance(db.connection, sqlite3.Connection)


def test_database_creation_success(db):

    assert os.path.exists(db.filename)


def test_database_creation_valid_db(db):

    conn = sqlite3.connect(db.filename)

    assert isinstance(conn, sqlite3.Connection)


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
def test_database_creation_correct_schema(db, case):

    rows = db.get_db_table_schema(case[0])

    assert rows == case[1]


@pytest.mark.parametrize('case', [
    (
        "servers",
        "ssh_port",
        [-2147483648, -350000, -100, -1, 0, 1, 100, 350000, 2147483647],
    ),
    (
        "servers",
        "ssh_user",
        ["", "a", "'a'", "3", "True", "xxxxxxxxxx", "mary had a little lamb"],
    ),
    (
        "servers",
        "last_sync_ok",
        [True, False],
    ),
    (
        "servers",
        "last_sync_err",
        [None],
    ),
    (
        "servers",
        "last_sync_attempt_time",
        [
            datetime.datetime(1900, 1, 1, 0, 0, 0),
            datetime.datetime(1960, 2, 4, 22, 3, 59),
            datetime.datetime(1969, 12, 31, 23, 59, 59),
            datetime.datetime(1970, 1, 1, 0, 0, 0),
            datetime.datetime(1985, 3, 29, 5, 19, 48),
            datetime.datetime(1999, 12, 31, 23, 59, 59),
            datetime.datetime(2000, 1, 1, 0, 0, 0),
            datetime.datetime(2001, 5, 30, 11, 17, 10),
            datetime.datetime(2019, 7, 18, 8, 0, 0),
            datetime.datetime(2025, 8, 23, 1, 0, 5),
            datetime.datetime(2145, 11, 11, 19, 38, 12)
        ],
    ),
])
def test_database_type_conversion(db, case):

    for value in case[2]:
        assert db.convert_db_to_col(db.convert_col_to_db(value, case[0], case[1]), case[0], case[1]) == value


def test_database_create_table_succeed(db):

    db.create_table("new_table", new_table_schema)

    new_table_rows = db.get_db_table_schema("new_table")

    db.connection.rollback()

    assert new_table_rows == [
        (0, "pk", "", 1, None, 1),
        (1, "blarg", "", 0, None, 0),
        (2, "snarf", "", 1, None, 0),
    ]


def test_database_create_table_fail_exists(db):

    with pytest.raises(ValueError):
        db.create_table("servers", new_table_schema)

    db.connection.rollback()


def test_database_create_table_fail_empty(db):

    with pytest.raises(ValueError):

        db.create_table("empty", dict({}))

    db.connection.rollback()


@pytest.mark.parametrize('data', [
    {
        "server_name":              "baldrick",
        "last_sync_attempt_time":   datetime.datetime(2019, 2, 22, 13, 45, 30),
        "last_sync_success_time":   datetime.datetime(2019, 2, 22, 14, 9, 11),
        "last_sync_ok":             True,
        "last_sync_err":            None,
        "ssh_port":                 22614,
        "ssh_user":                 "root"
    },
    {
        "server_name":              "weasel",
        "last_sync_attempt_time":   datetime.datetime(2019, 2, 24, 11, 5, 20),
        "last_sync_success_time":   datetime.datetime(2019, 2, 20, 1, 0, 20),
        "last_sync_ok":             False,
        "last_sync_err":            "Its broken",
        "ssh_port":                 22,
        "ssh_user":                 "root"
    },
    {
        "server_name":              "hufflepuff",
        "last_sync_attempt_time":   None,
        "last_sync_success_time":   None,
        "last_sync_ok":             None,
        "last_sync_err":            None,
        "ssh_port":                 None,
        "ssh_user":                 "root"
    },
    {
        "server_name":              "brian",
        "last_sync_attempt_time":   datetime.datetime(2018, 12, 22, 23, 9, 2),
        "last_sync_success_time":   datetime.datetime(2018, 12, 22, 23, 9, 2),
        "last_sync_ok":             True,
        "last_sync_err":            None,
        "ssh_port":                 22614,
        "ssh_user":                 "ssh_user"
    }
])
def test_database_insert_row(db, data):

    db.insert("servers", data)

    cur = db.connection.cursor()

    cur.execute(
        f"select server_name, last_sync_attempt_time, last_sync_success_time, last_sync_ok, last_sync_err,"
        f"ssh_port, ssh_user from servers where server_name='{data['server_name']}'"
    )

    rows = cur.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == data["server_name"]
    assert db.convert_db_to_col(rows[0][1], "servers", "last_sync_attempt_time") == data["last_sync_attempt_time"]
    assert db.convert_db_to_col(rows[0][2], "servers", "last_sync_success_time") == data["last_sync_success_time"]
    assert db.convert_db_to_col(rows[0][3], "servers", "last_sync_ok") == data["last_sync_ok"]
    assert db.convert_db_to_col(rows[0][4], "servers", "last_sync_err") == data["last_sync_err"]
    assert db.convert_db_to_col(rows[0][5], "servers", "ssh_port") == data["ssh_port"]
    assert db.convert_db_to_col(rows[0][6], "servers", "ssh_user") == data["ssh_user"]


def test_database_insert_row_fail_null(db):

    with pytest.raises(ValueError):
        db.insert("servers", {"server_name": None})

    db.connection.rollback()


def test_database_insert_row_fail_duplicate(db):

    with pytest.raises(sqlite3.IntegrityError):
        db.insert("servers", {"server_name": "baldrick"})

    db.connection.rollback()


def test_database_insert_row_fail_badcol(db):

    with pytest.raises(KeyError):
        db.insert("servers", {"abc": "baldrick"})

    db.connection.rollback()


def test_database_insert_row_fail_badtable(db):

    with pytest.raises(KeyError):
        db.insert("servers299", {"abc": "baldrick"})

    db.connection.rollback()


# noinspection PyTypeChecker
def test_database_insert_row_fail_notdict(db):

    with pytest.raises(TypeError):
        db.insert("servers299", 17)

    db.connection.rollback()


def test_database_insert_row_fail_mandatory(db):

    with pytest.raises(ValueError):
        db.insert("users", {"user_name": "brian"})

    db.connection.rollback()


@pytest.mark.parametrize('data', [
    {
        "server_name":              "baldrick",
    },
    {
        "server_name":              "weasel",
        "ssh_port":                 22,
    },
    {
        "server_name":              "hufflepuff",
        "ssh_user":                 "root"
    },
    {
        "server_name":              "brian",
        "last_sync_ok":             True,
    },
    {
        "server_name": "baldrick",
        "last_sync_attempt_time": datetime.datetime(2019, 2, 22, 13, 45, 30),
        "last_sync_success_time": datetime.datetime(2019, 2, 22, 14, 9, 11),
        "last_sync_ok": True,
        "last_sync_err": None,
        "ssh_port": 22614,
        "ssh_user": "root"
    },
    {
        "server_name": "weasel",
        "last_sync_attempt_time": datetime.datetime(2019, 2, 24, 11, 5, 20),
        "last_sync_success_time": datetime.datetime(2019, 2, 20, 1, 0, 20),
        "last_sync_ok": False,
        "last_sync_err": "Its broken",
        "ssh_port": 22,
        "ssh_user": "root"
    },
    {
        "server_name": "hufflepuff",
        "last_sync_attempt_time": None,
        "last_sync_success_time": None,
        "last_sync_ok": None,
        "last_sync_err": None,
        "ssh_port": None,
        "ssh_user": "root"
    },
    {
        "server_name": "brian",
        "last_sync_attempt_time": datetime.datetime(2018, 12, 22, 23, 9, 2),
        "last_sync_success_time": datetime.datetime(2018, 12, 22, 23, 9, 2),
        "last_sync_ok": True,
        "last_sync_err": None,
        "ssh_port": 22614,
        "ssh_user": "ssh_user"
    }
])
def test_database_select(db, data):

    rows = db.select("servers", data)

    assert len(rows) == 1

    for n, k in [
        (0, "server_name"),
        (1, "last_sync_attempt_time"),
        (2, "last_sync_success_time"),
        (3, "last_sync_ok"),
        (4, "last_sync_err"),
        (5, "ssh_port"),
        (6, "ssh_user"),
    ]:
        if k in data:
            assert db.convert_db_to_col(rows[0][n], "servers", k) == data[k]


@pytest.mark.parametrize('case', [
    (
            "servers",
            {
                "last_sync_err": None
            },
            [
                (
                        'baldrick',
                        '2019-02-22 13:45:30',
                        '2019-02-22 14:09:11',
                        1,
                        None,
                        22614,
                        'root'
                ),
                (
                        'hufflepuff',
                        None,
                        None,
                        None,
                        None,
                        None,
                        'root'
                ),
                (
                        'brian',
                        '2018-12-22 23:09:02',
                        '2018-12-22 23:09:02',
                        1,
                        None,
                        22614,
                        'ssh_user'
                )
            ],
    ),
    (
            "servers",
            {
                "ssh_user": "root"
            },
            [
                (
                        'baldrick',
                        '2019-02-22 13:45:30',
                        '2019-02-22 14:09:11',
                        1,
                        None,
                        22614,
                        'root'
                ),
                (
                        'weasel',
                        '2019-02-24 11:05:20',
                        '2019-02-20 01:00:20',
                        0,
                        'Its broken',
                        22,
                        'root'
                ),
                (
                        'hufflepuff',
                        None,
                        None,
                        None,
                        None,
                        None,
                        'root'
                )
            ],
    ),
    (
            "servers",
            {
                "ssh_port": 22614
            },
            [
                (
                        'baldrick',
                        '2019-02-22 13:45:30',
                        '2019-02-22 14:09:11',
                        1,
                        None,
                        22614,
                        'root'
                ),
                (
                        'brian',
                        '2018-12-22 23:09:02',
                        '2018-12-22 23:09:02',
                        1,
                        None,
                        22614,
                        'ssh_user'
                )
            ],
    ),
])
def test_database_select_multiple(db, case):

    rows = db.select(case[0], dict(case[1]))

    assert rows == case[2]


def test_database_update_row(db):

    db.update("servers", dict({"server_name": "baldrick"}), dict({"ssh_port": 99}))

    row = db.select("servers", {"server_name": "baldrick"})

    db.connection.rollback()

    assert len(row) == 1
    assert row[0][5] == 99


def test_database_update_row_fail_nonexist_table(db):

    with pytest.raises(KeyError):
        db.update("servers22", dict({"server_name": "baldrick"}), dict({"ssh_port": 99}))

    db.connection.rollback()


def test_database_update_row_fail_nonexist_column(db):

    with pytest.raises(KeyError):
        db.update("servers", dict({"server_name": "baldrick"}), dict({"xyzabc": 99}))

    db.connection.rollback()


# noinspection PyTypeChecker
def test_database_update_row_fail_bad_criteria(db):

    with pytest.raises(TypeError):
        db.update("servers", 77, dict({"xyzabc": 99}))

    db.connection.rollback()


# noinspection PyTypeChecker
def test_database_update_row_fail_bad_values(db):

    with pytest.raises(TypeError):
        db.update("servers", dict({"server_name": "baldrick"}), 42)

    db.connection.rollback()


def test_database_delete_row(db):

    db.delete("servers", dict({"server_name": "baldrick"}))

    rows = db.execute("select count(*) from servers where server_name=?", tuple(("baldrick",)))

    db.connection.rollback()

    assert rows == [(0,)]


def test_database_delete_row_fail_nonexist_table(db):

    with pytest.raises(KeyError):
        db.delete("servers99", dict({"server_name": "baldrick"}))

    db.connection.rollback()


def test_database_delete_row_fail_nonexist_field(db):

    with pytest.raises(KeyError):
        db.delete("servers", dict({"wibble": "baldrick"}))

    db.connection.rollback()


# noinspection PyTypeChecker
def test_database_delete_row_fail_bad_criteria(db):

    with pytest.raises(TypeError):
        db.delete("servers99", 7)

    db.connection.rollback()


@pytest.mark.parametrize('case', [
    (
            "select count(*) from servers",
            tuple(),
            [
                (3,)
            ]
    ),
    (
            "select sum(ssh_port) from servers",
            tuple(),
            [
                (22636,)
            ]
    ),
    (
            "select last_sync_err from servers order by last_sync_err",
            tuple(),
            [
                (None,),
                (None,),
                ("Its broken",),
            ]
    ),
    (
            "select server_name, last_sync_attempt_time, last_sync_ok, ssh_port from servers where ssh_user=?",
            tuple(("ssh_user",)),
            [
                ("brian", "2018-12-22 23:09:02", 1, 22614),
            ]
    ),
    (
            "update servers set last_sync_err = ? where server_name=?",
            tuple(("snarf", "brian")),
            [
            ]
    ),
    (
            "insert into servers (server_name, last_sync_ok, last_sync_err) values (?, ?, ?)",
            tuple(("test42", True, None)),
            [
            ]
    ),
    (
            "delete from servers where server_name=?",
            tuple(("baldrick",)),
            [
            ]
    ),
])
def test_execute(db, case):

    rows = db.execute(case[0], tuple(case[1]))
    db.connection.rollback()

    results = list(map(lambda r: tuple(r), rows))

    assert results == case[2]


@pytest.mark.parametrize('case', [
    (
            "blarg",
            tuple(),
            sqlite3.OperationalError
    ),
    (
            "select * from nanananana",
            tuple(),
            sqlite3.OperationalError
    ),
    (
            "update servers set ssh_port=? where server_name=?",
            tuple((100,)),
            sqlite3.ProgrammingError
    ),
    (
            "select notthere from servers",
            tuple(),
            sqlite3.OperationalError
    ),
    (
            "insert into servers (ssh_port) values (199)",
            tuple(),
            sqlite3.IntegrityError
    ),
    (
            None,
            tuple(),
            TypeError
    ),
    (
            17,
            tuple(),
            TypeError
    ),
    (
            "select * from servers",
            None,
            TypeError
    ),
    (
            "select * from servers",
            (1, 2, 3),
            sqlite3.ProgrammingError
    ),
    (
            "select * from servers",
            43,
            TypeError
    ),
])
def test_execute_fail(db, case):

    with pytest.raises(case[2]):

        db.execute(case[0], tuple(case[1]))

    db.connection.rollback()


@pytest.mark.parametrize('case', [
    (
        "insert into servers (server_name, ssh_port) values (?, ?)",
        [
            ("xxx", 1),
            ("yyy", 2),
            ("zzz", 3),
        ],
        "select server_name, ssh_port from servers where "
        "server_name = 'xxx' or server_name = 'yyy' or server_name = 'zzz'",
        (),
        [
            ("xxx", 1),
            ("yyy", 2),
            ("zzz", 3),
        ]
    ),
])
def test_executemany(db, case):

    db.executemany(case[0], list(case[1]))

    if case[2] is not None:

        rows = db.execute(case[2], tuple(case[3]))
        db.connection.rollback()
        assert rows == case[4]

    else:

        db.connection.rollback()


@pytest.mark.parametrize('case', [
    (
            "insert into servers (server_name, ssh_port) values (?, ?)",
            [
                ("xxx", 1),
                ("xxx", 2),
                ("yyy", 3),
                ("zzz", 4),
            ],
            sqlite3.IntegrityError,
    ),
    (
            "insert into servers (server_name, ssh_port) values (?, ?)",
            [
                ("xxx", 1, 33),
                ("yyy", 2, 55),
                ("zzz", 3, 99),
            ],
            sqlite3.ProgrammingError,
    ),
    (
            "insert into servers (server_name, ssh_port) values (?, ?)",
            [
                ("xxx",),
                ("yyy",),
                ("zzz",),
            ],
            sqlite3.ProgrammingError,
    ),
    (
            "insert into notexisting (server_name, ssh_port) values (?, ?)",
            [
                ("xxx", 1),
                ("yyy", 3),
                ("zzz", 4),
            ],
            sqlite3.OperationalError,
    ),
    (
            "fdgjhsdjfgh",
            [
                ("xxx", 1),
            ],
            sqlite3.OperationalError,
    ),

])
def test_executemany_fail(db, case):

    with pytest.raises(case[2]):

        db.executemany(case[0], list(case[1]))

    db.connection.rollback()
