import os
from datetime import datetime
from typing import Dict, Optional

from raw.util.database import Database, DatabaseField
from raw.web.secondary.defaults import *
from raw.web.secondary.config import SecondaryConfiguration


site_database_schema: Dict[str, Dict[str, DatabaseField]] = {
    "servers": {
        "server_name":
            DatabaseField(
                columnname="server_name",
                dbtype=str,
                pythontype=str,
                primarykey=True,
                nullable=False,
                description="Server Name"
            ),
        "last_sync_attempt_time":
            DatabaseField(
                columnname="last_sync_attempt_time",
                dbtype=str,
                pythontype=datetime,
                primarykey=False,
                nullable=True,
                description="Last Sync Attempt Time"
            ),
        "last_sync_success_time":
            DatabaseField(
                columnname="last_sync_success_time",
                dbtype=str,
                pythontype=datetime,
                primarykey=False,
                nullable=True,
                description="Last Sync Success Time"
            ),
        "last_sync_ok":
            DatabaseField(
                columnname="last_sync_ok",
                dbtype=int,
                pythontype=bool,
                primarykey=False,
                nullable=True,
                description="Last Sync Attempt Successful"
            ),
        "last_sync_err":
            DatabaseField(
                columnname="last_sync_err",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True,
                description="Last Sync Error"
            ),
        "ssh_port":
            DatabaseField(
                columnname="ssh_port",
                dbtype=int,
                pythontype=int,
                primarykey=False,
                nullable=True,
                description="SSH Port"
            ),
        "ssh_user":
            DatabaseField(
                columnname="ssh_user",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True,
                description="SSH User Name"
            )
    },
    "users": {
        "user_name":
            DatabaseField(
                columnname="user_name",
                dbtype=str,
                pythontype=str,
                primarykey=True,
                nullable=False,
                description="User Name"
            ),
        "master_server":
            DatabaseField(
                columnname="master_server",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=False,
                description="Master Server"
            ),
        "last_sync_attempt_time":
            DatabaseField(
                columnname="last_sync_attempt_time",
                dbtype=str,
                pythontype=datetime,
                primarykey=False,
                nullable=True,
                description="Last Sync Attempt Time"
            ),
        "last_sync_success_time":
            DatabaseField(
                columnname="last_sync_success_time",
                dbtype=str,
                pythontype=datetime,
                primarykey=False,
                nullable=True,
                description="Last Sync Success Time"
            ),
        "last_sync_ok":
            DatabaseField(
                columnname="last_sync_ok",
                dbtype=int,
                pythontype=bool,
                primarykey=False,
                nullable=True,
                description="Last Sync Successful"
            ),
        "last_sync_err":
            DatabaseField(
                columnname="last_sync_err",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True,
                description="Last Sync Error"
            ),
        "ssh_port":
            DatabaseField(
                columnname="ssh_port",
                dbtype=int,
                pythontype=int,
                primarykey=False,
                nullable=True,
                description="SSH Port"
            ),
        "ssh_user":
            DatabaseField(
                columnname="ssh_user",
                dbtype=str,
                pythontype=str,
                primarykey=False,
                nullable=True,
                description="SSH User Name"
            ),
        "implicit":
            DatabaseField(
                columnname="implicit",
                dbtype=int,
                pythontype=bool,
                primarykey=False,
                nullable=False,
                description="User Created Automatically"
            )
    }
}


class SiteDatabase(object):

    def __init__(
            self,
            config: SecondaryConfiguration,
            create: bool = False
    ):

        self.config = config
        self.database = Database(self.config.database_file, site_database_schema, create)


    def create_server(self, **kwargs):

        self.config.debug(f"SiteDatabase.create_server({kwargs.get('server_name')})")
        new_svr = Server(self, **kwargs)
        new_svr.insert()
        return new_svr


    def get_servers(self, **kwargs):

        self.config.debug(f"SiteDatabase.get_servers()")

        rows = self.database.select("servers", kwargs)

        result = list(map(lambda r: dict({
            "server_name":              self.database.convert_db_to_col(r[0], "servers", "server_name"),
            "last_sync_attempt_time":   self.database.convert_db_to_col(r[1], "servers", "last_sync_attempt_time"),
            "last_sync_success_time":   self.database.convert_db_to_col(r[2], "servers", "last_sync_success_time"),
            "last_sync_ok":             self.database.convert_db_to_col(r[3], "servers", "last_sync_ok"),
            "last_sync_err":            self.database.convert_db_to_col(r[4], "servers", "last_sync_err"),
            "ssh_port":                 self.database.convert_db_to_col(r[5], "servers", "ssh_port"),
            "ssh_user":                 self.database.convert_db_to_col(r[6], "servers", "ssh_user"),
        }), rows))

        return list(map(lambda s: Server(self, **s), result))


    def create_user(self, **kwargs):

        self.config.debug(f"SiteDatabase.create_user({kwargs.get('user_name')})")
        new_user = User(self, **kwargs)
        new_user.insert()
        return new_user


    def get_users(self, **kwargs):

        self.config.debug(f"SiteDatabase.get_users()")

        rows = self.database.select("users", kwargs)

        result = list(map(lambda r: dict({
            "user_name":                self.database.convert_db_to_col(r[0], "users", "user_name"),
            "master_server":            self.database.convert_db_to_col(r[1], "users", "master_server"),
            "last_sync_attempt_time":   self.database.convert_db_to_col(r[2], "users", "last_sync_attempt_time"),
            "last_sync_success_time":   self.database.convert_db_to_col(r[3], "users", "last_sync_success_time"),
            "last_sync_ok":             self.database.convert_db_to_col(r[4], "users", "last_sync_ok"),
            "last_sync_err":            self.database.convert_db_to_col(r[5], "users", "last_sync_err"),
            "ssh_port":                 self.database.convert_db_to_col(r[6], "users", "ssh_port"),
            "ssh_user":                 self.database.convert_db_to_col(r[7], "users", "ssh_user"),
            "implicit":                 self.database.convert_db_to_col(r[8], "users", "implicit"),
        }), rows))

        return list(map(lambda s: User(self, **s), result))


    def close(self):

        self.config.info(f"SiteDatabase.close()")
        self.database.close()


    def delete_file(self):

        self.config.info(f"SiteDatabase.delete_file({self.config.database_file})")
        os.remove(self.config.database_file)


class Server(object):

    def __init__(
            self,
            database: SiteDatabase,
            **kwargs
    ):

        if "server_name" not in kwargs:

            raise ValueError(f"server_name not specified but is required when Server() object instantiated")

        self.sitedb = database
        self.server_name: str = kwargs.get("server_name")
        self.last_sync_attempt_time: Optional[datetime] = kwargs.get("last_sync_attempt_time", None)
        self.last_sync_success_time: Optional[datetime] = kwargs.get("last_sync_success_time", None)
        self.last_sync_ok: Optional[bool] = kwargs.get("last_sync_ok", None)
        self.last_sync_err: Optional[str] = kwargs.get("last_sync_err", None)
        self.ssh_user: Optional[str] = kwargs.get("ssh_user", None)
        self.ssh_port: Optional[int] = kwargs.get("ssh_port", None)


    def asdict(self) -> dict:

        return dict({
            "server_name":                  self.server_name,
            "last_sync_attempt_time":       self.last_sync_attempt_time,
            "last_sync_success_time":       self.last_sync_success_time,
            "last_sync_ok":                 self.last_sync_ok,
            "last_sync_err":                self.last_sync_err,
            "ssh_user":                     self.ssh_user,
            "ssh_port":                     self.ssh_port,
        })


    def insert(self):

        self.sitedb.config.debug(f"Server.insert({self.server_name})")
        self.sitedb.database.insert(
            "servers",
            self.asdict()
        )


    def delete(self):

        self.sitedb.config.debug(f"Server.delete({self.server_name})")
        self.sitedb.database.delete(
            "servers",
            {"server_name": self.server_name}
        )


    def update(self):

        self.sitedb.config.debug(f"Server.update({self.server_name})")
        self.sitedb.database.update(
            "servers",
            {"server_name": self.server_name},
            self.asdict()
        )


class User(object):

    def __init__(
            self,
            database: SiteDatabase,
            **kwargs
    ):

        for k in ["user_name", "master_server", "implicit"]:

            if k not in kwargs:

                raise ValueError(f"{k} not specified but is required when User() object instantiated")

        self.sitedb = database
        self.user_name: str = kwargs.get("user_name")
        self.master_server: str = kwargs.get("master_server")
        self.last_sync_attempt_time: Optional[datetime] = kwargs.get("last_sync_attempt_time", None)
        self.last_sync_success_time: Optional[datetime] = kwargs.get("last_sync_success_time", None)
        self.last_sync_ok: Optional[bool] = kwargs.get("last_sync_ok", None)
        self.last_sync_err: Optional[str] = kwargs.get("last_sync_err", None)
        self.ssh_user: Optional[str] = kwargs.get("ssh_user", None)
        self.ssh_port: Optional[int] = kwargs.get("ssh_port", None)
        self.implicit: bool = kwargs.get("implicit")


    def asdict(self) -> dict:

        return dict({
            "user_name":                    self.user_name,
            "master_server":                self.master_server,
            "last_sync_attempt_time":       self.last_sync_attempt_time,
            "last_sync_success_time":       self.last_sync_success_time,
            "last_sync_ok":                 self.last_sync_ok,
            "last_sync_err":                self.last_sync_err,
            "ssh_user":                     self.ssh_user,
            "ssh_port":                     self.ssh_port,
            "implicit":                     self.implicit,
        })


    def insert(self):

        self.sitedb.config.debug(f"User.insert({self.user_name})")
        self.sitedb.database.insert(
            "users",
            self.asdict()
        )


    def delete(self):

        self.sitedb.config.debug(f"User.delete({self.user_name})")
        self.sitedb.database.delete(
            "users",
            {"user_name": self.user_name}
        )


    def update(self):

        self.sitedb.config.debug(f"User.update({self.user_name})")
        self.sitedb.database.update(
            "users",
            {"user_name": self.user_name},
            self.asdict()
        )
