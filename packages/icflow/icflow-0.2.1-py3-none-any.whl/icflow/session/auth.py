import logging
from functools import partial

from iccore.auth import User

from icflow.session.app import get_app, app_init

logger = logging.getLogger(__name__)


def user_add(name: str, email: str):

    User(name=name, email=email).save()


def user_list():
    return User.objects()


def user_login(username: str):

    get_app().login(username)


def user_add_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info(f"Adding user: {args.name}")
    user_add(args.name, args.email)


def user_list_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Listing users")
    users = user_list()
    for user in users:
        print(user.name)


def user_login_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Logging in user")
    user_login(args.username)


def add_user_parsers(subparsers, app_name: str = "icflow"):

    user_parser = subparsers.add_parser("user")
    user_subparsers = user_parser.add_subparsers(required=True)
    user_add_parser = user_subparsers.add_parser("add")
    user_add_parser.add_argument("--name", type=str, help="A unique user name")
    user_add_parser.add_argument("--email", type=str, help="User's email")
    user_add_parser.set_defaults(func=partial(user_add_cli, app_name))

    user_login_parser = user_subparsers.add_parser("login")
    user_login_parser.add_argument("--username", type=str, help="Login username")
    user_login_parser.set_defaults(func=partial(user_login_cli, app_name))

    user_list_parser = user_subparsers.add_parser("list")
    user_list_parser.set_defaults(func=partial(user_list_cli, app_name))
