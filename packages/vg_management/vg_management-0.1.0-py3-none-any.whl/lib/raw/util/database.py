import sqlite3
import os
import random
import time
from datetime import datetime
from collections import namedtuple
from typing import Dict, List, Optional, Union, Generator
import logging


DatabaseField = namedtuple('DatabaseField', 'columnname dbtype pythontype primarykey nullable description')


class Database(object):

    def __init__(
            self,
            filename: str,
            schema: Dict[str, Dict[str, DatabaseField]] = None,
            create: bool = False

    ):

        if not isinstance(filename, str):

            logging.error(f"Database.__init__(): filename must be str, not {str(type(filename))}")
            raise TypeError(f"filename must be str, not {str(type(filename))}")

        self.filename = filename

        if not isinstance(schema, dict):

            logging.error(f"Database.__init__(): schema must be dict, not {str(type(dict))}")
            raise TypeError(f"schema must be dict, not {str(type(dict))}")

        if len(schema) < 1:

            logging.error(f"Database.__init__(): schema cannot be empty")
            raise ValueError(f"schema cannot be empty")

        self.schema = schema

        self.connection = None

        if create:

            self._create()

        else:

            self._open()


    @classmethod
    def make_filename(
            cls,
            directory
    ):

        return f"{str(directory)}/db_{os.getpid()}_{time.time()}_{random.randint(0,100000)}"


    @classmethod
    def compare_column_definition(cls, n: int, col_defn: DatabaseField, db_col: sqlite3.Row):

        return (db_col[0] == n) and (db_col[1] == col_defn.columnname)


    def convert_col_to_db(
            self,
            value,
            table_name: str,
            column_name: str
    ) -> Optional[Union[int, str]]:

        if not isinstance(table_name, str):

            logging.error(f"Database.convert_col_to_db(): table_name must be str, not {str(type(table_name))}")
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        if not isinstance(column_name, str):

            logging.error(f"Database.convert_col_to_db(): column_name must be str, not {str(type(column_name))}")
            raise TypeError(f"column_name must be str, not {str(type(column_name))}")

        if table_name not in self.schema:

            logging.error(f"Database.convert_col_to_db(): Table {table_name} does not exist in schema")
            raise KeyError(
                f"Table {table_name} does not exist in schema"
            )

        if column_name not in self.schema[table_name]:

            logging.error(f"Database.convert_col_to_db(): Column {column_name} does not exist in table {table_name}")
            raise KeyError(
                f"Column {column_name} does not exist in table {table_name}"
            )

        col = self.schema[table_name][column_name]

        if value is None and not col.nullable:

            logging.error(
                f"Database.convert_col_to_db(): Table {table_name} column {column_name} "
                f"does not allow NULL (None) values"
            )
            raise ValueError(
                f"Table {table_name} column {column_name} does not allow NULL (None) values"
            )

        if not (isinstance(value, col.pythontype) or (value is None and col.nullable)):

            logging.error(
                f"Database.convert_col_to_db(): Values for table {table_name} column {column_name} must be"
                f" {str(col.pythontype)} not {str(type(value))}"

            )
            raise TypeError(
                f"Values for table {table_name} column {column_name} must be"
                f" {str(col.pythontype)} not {str(type(value))}"
            )

        if value is None:

            return None

        if col.pythontype is int or col.pythontype is str:

            return value

        elif col.pythontype is bool:

            if value:

                return 1

            return 0

        elif col.pythontype is datetime:

            return value.strftime("%Y-%m-%d %H:%M:%S")

        else:

            logging.error(
                f"Database.convert_col_to_db(): Handling of column type {str(type(col.pythontype))} not implemented"
            )
            raise NotImplementedError(f"Handling of column type {str(type(col.pythontype))} not implemented")


    def convert_db_to_col(
            self,
            value,
            table_name,
            column_name
    ) -> Optional[Union[int, str, bool, datetime]]:

        if not isinstance(table_name, str):

            logging.error(f"Database.convert_db_to_col(): table_name must be str, not {str(type(table_name))}")
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        if not isinstance(column_name, str):

            logging.error(f"Database.convert_db_to_col(): column_name must be str, not {str(type(column_name))}")
            raise TypeError(f"column_name must be str, not {str(type(column_name))}")

        if value is None:
            return None

        if table_name not in self.schema:

            logging.error(f"Database.convert_db_to_col(): Table {table_name} does not exist in schema")
            raise KeyError(
                f"Table {table_name} does not exist in schema"
            )

        if column_name not in self.schema[table_name]:

            raise KeyError(
                f"Column {column_name} does not exist in table {table_name}"
            )

        col = self.schema[table_name][column_name]

        if col.pythontype is bool:

            return value != 0

        elif col.pythontype is int:

            return int(value)

        elif col.pythontype is str:

            return str(value)

        elif col.pythontype is datetime:

            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

        else:

            logging.error(
                f"Database.convert_db_to_col(): Python data type {str(type(col.pythontype))} not implemented"
            )
            raise NotImplementedError(f"Handling of python data type {str(type(col.pythontype))} not implemented")


    def get_db_table_schema(self, table_name: str) -> List[sqlite3.Row]:

        if not isinstance(table_name, str):

            logging.error(f"Database.get_db_table_schema(): table_name must be str, not {str(type(table_name))}")
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        sql = f"pragma table_info('{table_name}')"
        logging.debug(f"Database.get_db_table_schema(): SQL: {sql}")

        return self.connection.execute(sql).fetchall()


    def validate_schema(self):

        if self.schema is None or not isinstance(self.schema, dict) or len(self.schema) < 1:

            logging.error(f"Database.validate_schema(): Schema is invalid - either None, wrong type or empty")
            raise RuntimeError(f"Schema is invalid - either None, wrong type or empty")

        # Iterate through tables in schema definition
        for defined_table in self.schema.keys():

            # Get schema for table from database
            db_table_schema: List[sqlite3.Row] = self.get_db_table_schema(defined_table)

            # Get schema for table from schema definition
            defined_table_schema: Dict[str, DatabaseField] = self.schema[defined_table]

            # Verify that both have the same number of entries
            if len(db_table_schema) != len(defined_table_schema):

                logging.error(
                    f"Database.validate_schema(): Schema mismatch between database ({len(db_table_schema)} cols)"
                    f" and definition ({len(defined_table_schema)} cols) for table '{defined_table}'"

                )
                raise RuntimeError(
                    f"Schema mismatch between database ({len(db_table_schema)} cols)"
                    f" and definition ({len(defined_table_schema)} cols) for table '{defined_table}'"
                )

            for n in range(0, len(defined_table_schema)-1):

                if db_table_schema[n][0] != n:

                    logging.error(
                        f"Database.validate_schema(): Column {n} of table '{defined_table}' in database"
                        f" has incorrect ordinal {db_table_schema[n][0]}"
                    )
                    raise RuntimeError(
                        f"Column {n} of table '{defined_table}' in database"
                        f" has incorrect ordinal {db_table_schema[n][0]}"
                    )

                if db_table_schema[n][1] not in defined_table_schema:

                    logging.error(
                        f"Database.validate_schema(): Database column '{db_table_schema[n][1]}' does not exist "
                        f"in definition of table {defined_table}"

                    )
                    raise RuntimeError(
                        f"Database column '{db_table_schema[n][1]}' does not exist "
                        f"in definition of table {defined_table}"
                    )

                if [True, False][db_table_schema[n][3]] != defined_table_schema[db_table_schema[n][1]].nullable:

                    logging.error(
                        f"Database.validate_schema(): Nullable property of column {db_table_schema[n][1]} in table "
                        f" {defined_table} mismatch between database and definition."

                    )
                    raise RuntimeError(
                        f"Nullable property of column {db_table_schema[n][1]} in table {defined_table} mismatch"
                        f" between database and definition."
                    )

                if [False, True][db_table_schema[n][5]] != defined_table_schema[db_table_schema[n][1]].primarykey:

                    logging.error(
                        f"Database.validate_schema(): PrimaryKey property of column {db_table_schema[n][1]} in "
                        f"table {defined_table} mismatch between database and definition."
                    )
                    raise RuntimeError(
                        f"PrimaryKey property of column {db_table_schema[n][1]} in in table {defined_table} "
                        f"mismatch between database and definition."
                    )


    def create_table(self, table_name: str):

        def opt_pk(col: DatabaseField) -> str:

            if col.primarykey:
                return "primary key"

            return ""

        def opt_null(col: DatabaseField) -> str:

            if col.nullable:
                return ""

            return "not null"

        if not isinstance(table_name, str):

            logging.error(
                f"Database.create_table(): table_name must be str, not {str(type(table_name))}"
            )
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        if table_name not in self.schema:

            logging.error(
                f"Database.create_table(): Database table '{table_name}' is not defined"

            )
            raise ValueError(
                f"Database table '{table_name}' is not defined"
            )

        if len(self.schema[table_name]) < 1:

            logging.error(
                f"Database.create_table(): schema for table {table_name} is empty"
            )
            raise ValueError(f"schema for table {table_name} is empty")

        cols = ""

        for col_name in self.schema[table_name].keys():

            if cols != "":
                cols += ", "

            cols += f"{col_name} {opt_pk(self.schema[table_name][col_name])}"\
                    f" {opt_null(self.schema[table_name][col_name])} "

        sql = f"create table {table_name} ({cols})"

        logging.debug(f"Database.create_table(): SQL: {sql}")

        self.connection.execute(sql)

        self.connection.commit()


    def _create(self):

        logging.warning(
            f"Database._create(): Creating database file '{self.filename}'"
        )

        if not isinstance(self.schema, dict):

            logging.error(
                f"Database._create(): schema must be dict, not {str(type(self.schema))}"
            )
            raise TypeError(f"schema must be dict, not {str(type(self.schema))}")

        self.connection = sqlite3.connect(self.filename)

        for table_name in self.schema.keys():

            self.create_table(table_name)

        self.validate_schema()


    def _open(self):

        logging.info(
            f"Database._open(): Opening database file '{self.filename}'"
        )

        if not os.path.exists(self.filename):

            logging.error(
                f"Database._open(): Database file '{self.filename}' does not exist"
            )
            raise ValueError(f"Database file '{self.filename}' does not exist")

        self.connection = sqlite3.connect(self.filename)

        self.validate_schema()


    def close(self):

        logging.info(
            f"Database.close(): Closing database file"
        )

        self.connection.close()


    def delete_file(self):

        logging.warning(
            f"Database.delete_file(): Deleting database file '{self.filename}'"
        )

        os.remove(self.filename)


    def insert(self, table_name: str, new_row: dict):

        if not isinstance(table_name, str):

            logging.error(
                f"Database.insert(): table_name must be str, not {str(type(table_name))}"
            )
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        if not isinstance(new_row, dict):

            logging.error(
                f"Database.insert(): new_row must be dict, not {str(type(new_row))}"
            )
            raise TypeError(f"new_row must be dict, not {str(type(new_row))}")

        if table_name not in self.schema:

            logging.error(
                f"Database.insert(): Table {table_name} does not exist in database"
            )
            raise KeyError(
                f"Table {table_name} does not exist in database"
            )

        if new_row is None or (not isinstance(new_row, dict)) or len(new_row) < 1:

            logging.error(
                f"Database.insert(): new_row must be nonempty dict of field/value pairs."
            )
            raise ValueError(
                f"new_row must be nonempty dict of field/value pairs."
            )

        fieldnames: List[str] = list()
        values: List[Optional[Union[str, int]]] = list()

        for fieldname in new_row.keys():

            if fieldname not in self.schema[table_name]:

                logging.error(
                    f"Database.insert(): Field '{fieldname}' does not exist in table '{table_name}'"
                )

                raise KeyError(
                    f"Field '{fieldname}' does not exist in table '{table_name}'"
                )

            fieldnames.append(fieldname)
            values.append(self.convert_col_to_db(
                new_row[fieldname],
                table_name,
                fieldname
            ))

        for fieldname in self.schema[table_name].keys():

            missing_mandatory: List[str] = list()

            if ((self.schema[table_name][fieldname].primarykey or not self.schema[table_name][fieldname].nullable) and
               fieldname not in fieldnames):

                missing_mandatory.append(fieldname)

            if len(missing_mandatory) > 0:

                logging.error(
                    f"Database.insert(): Mandatory field(s) {', '.join(missing_mandatory)} not specified."
                )

                raise ValueError(
                    f"Mandatory field(s) {', '.join(missing_mandatory)} not specified."
                )

        sql = f"insert into {table_name} ({', '.join(fieldnames)}) values ({', '.join(map(lambda x: '?', fieldnames))})"

        logging.debug(
            f"Database.insert(): SQL: {sql}"
        )

        self.connection.execute(sql, tuple(values))

        self.connection.commit()


    def delete(self, table_name: str, criteria: dict):

        if not isinstance(table_name, str):

            logging.error(
                f"Database.delete(): table_name must be str, not {str(type(table_name))}"
            )
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        if not isinstance(criteria, dict):

            logging.error(
                f"Database.delete(): criteria must be dict, not {str(type(criteria))}"
            )
            raise TypeError(f"criteria must be dict, not {str(type(criteria))}")

        if table_name not in self.schema:

            logging.error(
                f"Database.delete(): Table {table_name} does not exist in database"
            )
            raise KeyError(
                f"Table {table_name} does not exist in database"
            )

        where_values: List[Optional[Union[str, int]]] = list()

        if criteria is None or len(criteria) < 1:

            where_sql = ""

        else:

            where_fields: List[str] = list()

            for fieldname in criteria.keys():

                if fieldname not in self.schema[table_name]:

                    logging.error(
                        f"Database.delete(): Field '{fieldname}' does not exist in table '{table_name}'"
                    )
                    raise KeyError(
                        f"Field '{fieldname}' does not exist in table '{table_name}'"
                    )

                where_fields.append(fieldname)
                where_values.append(self.convert_col_to_db(
                    criteria[fieldname],
                    table_name,
                    fieldname
                ))

            where_sql = f"where {', '.join(map(lambda x: f'{x} = ?', where_fields))}"

        sql = f"delete from {table_name} {where_sql}"

        logging.debug(
            f"Database.delete(): SQL: {sql}"
        )

        self.connection.execute(sql, tuple(where_values))

        self.connection.commit()


    def update(self, table_name: str, criteria: dict, values: dict):

        if not isinstance(table_name, str):

            logging.error(
                f"Database.update(): table_name must be str, not {str(type(table_name))}"
            )
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        if not isinstance(criteria, dict):

            logging.error(
                f"Database.update(): criteria must be dict, not {str(type(criteria))}"
            )
            raise TypeError(f"criteria must be dict, not {str(type(criteria))}")

        if not isinstance(values, dict):

            logging.error(
                f"Database.update(): values must be dict, not {str(type(values))}"
            )
            raise TypeError(f"values must be dict, not {str(type(values))}")

        if table_name not in self.schema:

            logging.error(
                f"Database.update(): Table {table_name} does not exist in database"
            )
            raise KeyError(
                f"Table {table_name} does not exist in database"
            )

        if values is None or (not isinstance(values, dict)) or len(values) < 1:

            logging.error(
                f"Database.update(): New values must be a nonempty dict"
            )
            raise ValueError(
                f"New values must be a nonempty dict"
            )

        update_values: List[Optional[Union[str, int]]] = list()
        update_fields: List[str] = list()

        for fieldname in values.keys():

            if fieldname not in self.schema[table_name]:

                logging.error(
                    f"Database.update(): Field '{fieldname}' does not exist in table '{table_name}'"
                )
                raise KeyError(
                    f"Field '{fieldname}' does not exist in table '{table_name}'"
                )

            update_fields.append(fieldname)
            update_values.append(self.convert_col_to_db(
                values[fieldname],
                table_name,
                fieldname
            ))

        set_sql = f"set {', '.join(map(lambda x: f'{x} = ?', update_fields))} "

        where_values: List[Optional[Union[str, int]]] = list()

        if criteria is None or len(criteria) < 1:

            where_sql = ""

        else:

            where_fields: List[str] = list()

            for fieldname in criteria.keys():

                if fieldname not in self.schema[table_name]:

                    logging.error(
                        f"Database.update(): Field '{fieldname}' does not exist in table '{table_name}'"
                    )
                    raise ValueError(
                        f"Field '{fieldname}' does not exist in table '{table_name}'"
                    )

                where_fields.append(fieldname)
                where_values.append(self.convert_col_to_db(
                    criteria[fieldname],
                    table_name,
                    fieldname
                ))

            where_sql = f"where {', '.join(map(lambda x: f'{x} = ?', where_fields))}"

        sql = f"update {table_name} {set_sql} {where_sql}"

        logging.debug(
            f"Database.update(): SQL: {sql}"
        )

        self.connection.execute(sql, tuple(update_values + where_values))

        self.connection.commit()


    def select(self, table_name: str, criteria: dict) -> List[sqlite3.Row]:

        if not isinstance(table_name, str):

            logging.error(
                f"Database.select(): table_name must be str, not {str(type(table_name))}"
            )
            raise TypeError(f"table_name must be str, not {str(type(table_name))}")

        if not isinstance(criteria, dict):

            logging.error(
                f"Database.select(): criteria must be dict, not {str(type(criteria))}"
            )
            raise TypeError(f"criteria must be dict, not {str(type(criteria))}")

        if table_name not in self.schema:

            logging.error(
                f"Database.select(): Table {table_name} does not exist in database"
            )
            raise KeyError(
                f"Table {table_name} does not exist in database"
            )

        where_values: List[Optional[Union[str, int]]] = list()

        if criteria is None or len(criteria) < 1:

            where_sql = ""

        else:

            where_fields: List[str] = list()

            for fieldname in criteria.keys():

                if fieldname not in self.schema[table_name]:

                    logging.error(
                        f"Database.select(): Field '{fieldname}' does not exist in table '{table_name}'"
                    )
                    raise KeyError(
                        f"Field '{fieldname}' does not exist in table '{table_name}'"
                    )

                if criteria[fieldname] is None:

                    where_fields.append(f"{fieldname} is null")

                else:

                    where_fields.append(f"{fieldname} = ?")
                    where_values.append(self.convert_col_to_db(
                        criteria[fieldname],
                        table_name,
                        fieldname
                    ))

            where_sql = f"where {' and '.join(where_fields)}"

        sql = f"select * from {table_name} {where_sql}"

        logging.debug(
            f"Database.select(): SQL: {sql}"
        )

        cur = self.connection.cursor()

        cur.execute(sql, tuple(where_values))

        result = cur.fetchall()

        cur.close()

        return result


    def execute(self, sql: str, args: tuple) -> List[sqlite3.Row]:

        if not isinstance(sql, str):

            logging.error(
                f"Database.execute(): sql must be str, not {str(type(sql))}"
            )
            raise TypeError(f"sql must be str, not {str(type(sql))}")

        if not isinstance(args, tuple):

            logging.error(
                f"Database.execute(): args must be tuple, not {str(type(args))}"
            )
            raise TypeError(f"args must be tuple, not {str(type(args))}")

        cur = self.connection.cursor()

        logging.debug(
            f"Database.execute(): SQL: {sql} ARGS: {args}"
        )

        result = cur.execute(sql, args).fetchall()

        cur.close()

        return result


    def executemany(self, sql: str, args: Union[List[tuple], Generator]):

        if not isinstance(sql, str):

            logging.error(
                f"Database.executemany(): sql must be str, not {str(type(sql))}"
            )
            raise TypeError(f"sql must be str, not {str(type(sql))}")

        cur = self.connection.cursor()

        logging.debug(
            f"Database.executemany(): SQL: {sql}"
        )

        cur.executemany(sql, args)

        cur.close()

