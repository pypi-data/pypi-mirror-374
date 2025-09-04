from pathlib import Path
import logging
from functools import partial

from icflow.session import app_init
from icflow.data import (
    product_add,
    product_list,
    product_delete,
    dataset_add,
    dataset_list,
    dataset_delete,
    unit_add,
    unit_list,
)

logger = logging.getLogger(__name__)


def product_add_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Adding product")
    product_add(args.path.resolve())


def product_list_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Listing products")
    products = product_list()
    for p in products:
        print(p.name, p.added_by, p.x, p.y)


def product_delete_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Deleting product")
    product_delete(args.id)


def dataset_add_cli(app_name: str, args, data_load_funcs=None):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Adding dataset")
    dataset_add(args.spec.resolve(), args.path.resolve(), data_load_funcs)


def dataset_list_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Listing datasets")
    print("Id \tProduct \tAdded By \tPath \tStarts At \tEnds At")
    for d in dataset_list():
        print(
            f"{d.id}\t{d.product}\t{d.added_by}"
            f"\t{d.original_path}\t{d.start_datetime}\t{d.end_datetime}"
        )


def dataset_delete_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Deleting dataset")
    dataset_delete(args.id)


def unit_add_cli(app_name: str, args):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Adding units")
    unit_add(args.path.resolve())


def unit_list_cli(app_name: str):

    logger.info("Initializing app")
    app_init(name=app_name)

    logger.info("Listing units")
    unit_list()


def add_data_parsers(subparsers, app_name: str = "icflow", data_load_funcs=None):

    product_parser = subparsers.add_parser("product")
    product_subparsers = product_parser.add_subparsers(required=True)
    product_add_parser = product_subparsers.add_parser("add")
    product_add_parser.add_argument("--path", type=Path, help="Product path")
    product_add_parser.set_defaults(func=partial(product_add_cli, app_name))

    product_list_parser = product_subparsers.add_parser("list")
    product_list_parser.set_defaults(func=partial(product_list_cli, app_name))

    product_delete_parser = product_subparsers.add_parser("delete")
    product_delete_parser.add_argument("id", type=str, help="Product id to delete")
    product_delete_parser.set_defaults(func=partial(product_delete_cli, app_name))

    dataset_parser = subparsers.add_parser("dataset")
    dataset_subparsers = dataset_parser.add_subparsers(required=True)
    dataset_add_parser = dataset_subparsers.add_parser("add")
    dataset_add_parser.add_argument("--spec", type=Path, help="Dataset spec path")
    dataset_add_parser.add_argument("--path", type=Path, help="Dataset files path")
    dataset_add_parser.set_defaults(
        func=partial(dataset_add_cli, app_name, data_load_funcs=data_load_funcs)
    )

    dataset_list_parser = dataset_subparsers.add_parser("list")
    dataset_list_parser.set_defaults(func=partial(dataset_list_cli, app_name))

    dataset_delete_parser = dataset_subparsers.add_parser("delete")
    dataset_delete_parser.add_argument("id", type=int, help="Dataset id to delete")
    dataset_delete_parser.set_defaults(func=partial(dataset_delete_cli, app_name))

    unit_parser = subparsers.add_parser("unit")
    unit_subparsers = unit_parser.add_subparsers(required=True)
    unit_add_parser = unit_subparsers.add_parser("add")
    unit_add_parser.add_argument("--path", type=Path, help="Unit path")
    unit_add_parser.set_defaults(func=partial(unit_add_cli, app_name))

    unit_list_parser = unit_subparsers.add_parser("list")
    unit_list_parser.set_defaults(func=partial(unit_list_cli, app_name))
