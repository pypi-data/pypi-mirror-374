import logging
from functools import partial
from pathlib import Path

from icflow.session import app_init, system_init

from .report import report_generate

logger = logging.getLogger(__name__)


def system_init_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Initializing system")
    system_init()


def report_cli(app_name: str, args, load_funcs=None):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Generating report")
    report_generate(args.path.resolve(), args.work_dir.resolve(), load_funcs)


def add_system_parsers(subparsers, app_name: str = "icflow"):

    system_parser = subparsers.add_parser("system")
    system_subparsers = system_parser.add_subparsers(required=True)
    system_init_parser = system_subparsers.add_parser("init")
    system_init_parser.set_defaults(func=partial(system_init_cli, app_name))


def add_report_parsers(subparsers, app_name: str = "icflow", load_funcs=None):

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument(
        "--path", type=Path, help="Path to the report definition"
    )
    report_parser.add_argument("--work_dir", type=Path, help="Path to store output in")
    report_parser.set_defaults(
        func=partial(report_cli, app_name, load_funcs=load_funcs)
    )
