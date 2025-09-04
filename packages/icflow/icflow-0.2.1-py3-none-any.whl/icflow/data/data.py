from pathlib import Path
import hashlib
import logging

import yaml

from iccore.data import (
    ProductCreate,
    Product,
    ProductPublic,
    ProductPublicWithMeasurements,
    DatasetCreate,
    Dataset,
    DatasetPublic,
    Unit,
    UnitCreate,
    UnitPublic,
)
from iccore.serialization import json_utils
from iccore.filesystem import get_csv_files

from icflow import session
from icflow.data import csv, netcdf

logger = logging.getLogger(__name__)


def load(path: Path, item_t):

    if path.suffix in (".yaml" or ".yml"):
        with open(path, "r", encoding="utf-8") as f:
            docs = yaml.safe_load_all(f)
            items = [item_t(**d) for d in docs]

        return items

    if path.suffix == ".json":
        model_json = json_utils.read_json(path)
        if len(model_json) == 1 and "items" in model_json:
            return [item_t(**item) for item in model_json["items"]]
        return [item_t(**model_json)]

    raise RuntimeError(f"Path extension {path.suffix} not supported.")


def product_add(path: Path):

    products = load(path, ProductCreate)

    user = session.app.get_app().logged_in_user
    if not user:
        raise RuntimeError("No user logged in")

    for p in products:
        db_product = Product.from_create(p)
        db_product.added_by = user.name
        db_product.save()


def product_list() -> list[ProductPublic]:

    return Product().objects()


def product_delete(name: str):
    Product.delete_item(name, "name")


def get_checksum(path: Path) -> str:
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def check_duplicates(checksums: list[str]) -> list[bool]:

    return [
        bool(Dataset.object(c, "checksum", fail_on_none=False) is None)
        for c in checksums
    ]


def exluded_extension(path: Path, excludes: list[str]):
    path_suffixes = path.name.split(".")
    for p in path_suffixes:
        if p in excludes:
            return True
    return False


def has_extension(path: Path, extensions: list[str], excludes: list[str]):

    if exluded_extension(path, excludes):
        return False

    path_suffixes = path.name.split(".")
    for p in path_suffixes[1:]:
        for e in extensions:
            if p.lower() == e.lower():
                return True
    return False


def dataset_add(spec: Path, path: Path, load_funcs=None):

    dataset = load(spec, DatasetCreate)[0]

    user = session.app.get_app().logged_in_user
    if not user:
        raise RuntimeError("No user logged in")

    # Find candidate files
    if path.is_file():
        files = [path]
    elif dataset.file_format == "csv":
        files = get_csv_files(path)
    elif dataset.file_format == "netcdf":
        files = netcdf.get_files_recursive(path, ("nc", "nc.gz"))
    else:
        raise RuntimeError("Requested dataset format not supported")

    if dataset.extension_includes:
        files = [
            f
            for f in files
            if has_extension(f, dataset.extension_includes, dataset.path_excludes)
        ]

    # Get checksums
    checksums = [get_checksum(f) for f in files]

    # Find new files
    new_file_mask = check_duplicates(checksums)

    new_files = [
        (c, f) for is_new, c, f in zip(new_file_mask, checksums, files) if is_new
    ]

    logger.info("Adding %d new files", len(new_files))

    for checksum, f in new_files:

        product = Product.object(
            dataset.product, "name", return_t=ProductPublicWithMeasurements
        )

        # Index new files
        if dataset.file_format == "csv":
            series = csv.load(f, dataset, product)
        elif dataset.file_format == "netcdf":
            series = netcdf.load(f, dataset, product, load_funcs.get(dataset.name))
        else:
            raise RuntimeError("Requested dataset format not supported")

        start_time, end_time = series.get_x_bounds()

        # Register new files
        db_dataset = Dataset.from_create(dataset)
        db_dataset.original_path = str(f)
        db_dataset.checksum = checksum
        db_dataset.added_by = user.name
        db_dataset.start_datetime = start_time
        db_dataset.end_datetime = end_time
        db_dataset.save()


def dataset_list() -> list[DatasetPublic]:
    return Dataset.objects()


def dataset_delete(id: int):
    Dataset.delete_item(id)


def unit_add(path: Path):

    units = load(path, UnitCreate)

    for u in units:
        db_unit = u.to_model()
        db_unit.save()


def unit_list() -> list[UnitPublic]:
    return Unit.objects()
