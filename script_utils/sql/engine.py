from dataclasses import dataclass
from dotenv import dotenv_values
from sqlalchemy import create_engine, URL, Engine

from script_utils.sql.consts import (
    MYSQL_DEFAULT_PORT,
    MYSQL_DEFAULT_DATABASE,
    MYSQL_DRIVERNAME,
    MYSQL_DOTENV_USER,
    MYSQL_DOTENV_PASSWORD,
    MYSQL_DOTENV_PORT,
    MYSQL_DOTENV_DATABASE,
)


@dataclass
class ConnectionConfig:
    user: str
    password: str  # Is there a better way than storing this here?
    database: str | None = None
    port: int | None = None

    def __post_init__(self):
        if self.database is None:
            self.database = MYSQL_DEFAULT_DATABASE
        if self.port is None:
            self.port = MYSQL_DEFAULT_PORT

    @staticmethod
    def from_dotenv_file(dotenv_path : str | None = None) -> "ConnectionConfig":
        """
        Reads arguments from `.env` file, which is the preferred way, to avoid
        hardcoding sensitive information in the source code.

        Variable names in `.env` are provided in `MYSQL_DOTENV_*` constants.

        :return: New :class:`ConnectionConfig` object
        """
        config = dotenv_values(dotenv_path=dotenv_path)
        port = config.get(MYSQL_DOTENV_PORT)
        if port is not None:
            port = int(port)
        return ConnectionConfig(
            user=config.get(MYSQL_DOTENV_USER),
            password=config.get(MYSQL_DOTENV_PASSWORD),
            database=config.get(MYSQL_DOTENV_DATABASE),
            port=port,
        )

    def sql_alchemy_url(self) -> URL:
        """
        @return URL for creating SQLAlchemy engine
        """
        return URL.create(
            drivername=MYSQL_DRIVERNAME,
            username=self.user,
            password=self.password,
            host="localhost",
            port=self.port,
            database=self.database,
        )


def get_database_engine(
    config: ConnectionConfig | None = None,
    echo: bool = False,
) -> Engine:
    """
    Creates `SQLAlchemy` engine object from a connection config `config`. If not
    provided, the config arguments are read from a `.env` file (preferred).

    TODO: Catch errors!

    :param config: See above
    :param echo: Should engine write log messages to `stdout`?
    :return: :class:`Engine` object
    """
    if config is None:
        config = ConnectionConfig.from_dotenv_file()
    return create_engine(config.sql_alchemy_url(), echo=echo)
