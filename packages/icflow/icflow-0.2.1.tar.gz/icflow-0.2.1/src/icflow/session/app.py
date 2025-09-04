"""
This module is for workflow sessions
"""

import os
from pathlib import Path
import logging
from typing import cast

from iccore.auth import User, UserPublic
from iccore import time_utils
from iccore.database import create_db_engine, init_db
from iccore.serialization import yaml_utils
from iccore.system.environment import Environment

import icflow
from icflow.config import Config, get_default_config

logger = logging.getLogger(__name__)


def get_config(config_path: Path | None = None) -> Config:
    if config_path:
        config = yaml_utils.read_model_yaml(config_path, Config)
    else:
        config = get_default_config()
    return cast(Config, config)


class App:
    """
    An instance of the running application
    """

    def __init__(
        self,
        env: Environment,
        config_path: Path | None,
        work_dir: Path = Path(),
        name: str = "icflow",
        db_connect_args: dict | None = None,
    ):

        self.env = env
        self.work_dir = work_dir
        self.name = name
        self.logged_in_user: UserPublic | None = None
        self.cache_dir = self._get_cache_dir()
        self.db_connected = False
        self.db_connect_args = db_connect_args
        self.config = get_config(config_path)

    def _get_cache_dir(self) -> Path:
        env_cache = f"{self.name.upper()}_CACHE_DIR"
        env_cache_dir = os.getenv(env_cache)
        if env_cache_dir:
            return Path(env_cache_dir)
        return Path().home() / ".cache" / self.name

    def login(self, username: str):

        logger.info("Logging in user")
        self.logged_in_user = User.object(username, "name")
        if not self.logged_in_user:
            raise RuntimeError(f"Failed to log in user {username}")

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        with open(self.cache_dir / "user", "w", encoding="utf-8") as f:
            f.write(self.logged_in_user.name)

    def logout(self):
        user_cache = self.cache_dir / "user"
        if user_cache.exists():
            user_cache.unlink()

    def load(self):
        self.db_connect()
        self._try_load_user()

    def _try_load_user(self):
        userfile = self.cache_dir / "user"
        if userfile.exists():
            with open(userfile, "r", encoding="utf-8") as f:
                username = f.read()
            self.logged_in_user = User.object(username, "name")

    def db_connect(self):

        logger.info("Connecting to db")

        if self.config.db_url:
            db_url = self.config.db_url
        else:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            db_url = "sqlite:///" + str(self.cache_dir / "sqlite.db")

        create_db_engine(db_url, self.db_connect_args)
        self.db_connected = True


_APP: App | None = None


def app_init(
    env: Environment | None = None,
    work_dir: Path = Path(),
    config_path: Path | None = None,
    name: str = "icflow",
    db_connect_args: dict | None = None,
):

    global _APP
    working_env = env
    if not working_env:
        working_env = icflow.environment.load()

    _APP = App(
        env=working_env,
        config_path=config_path,
        work_dir=work_dir,
        name=name,
        db_connect_args=db_connect_args,
    )
    _APP.load()


def system_init():

    if not _APP:
        raise RuntimeError("Need to initialize session before initializing system.")

    logger.info("Initializing db")
    init_db()


def get_app() -> App:
    if not _APP:
        raise RuntimeError("Requested app not initialized yet")

    return _APP


def _setup_result_dir(result_dir: Path):
    """
    Utility to create a result directory with a timestamp
    -based name.
    """
    current_time = time_utils.get_timestamp_for_paths()
    result_dir = result_dir / Path(current_time)
    os.makedirs(result_dir, exist_ok=True)
    return result_dir
