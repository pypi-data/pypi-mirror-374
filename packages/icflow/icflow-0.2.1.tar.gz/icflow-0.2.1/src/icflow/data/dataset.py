"""
This module has functionaly for handling generic datasets.
"""

from pathlib import Path
import logging
from datetime import datetime
from typing import Callable

from pydantic import BaseModel

from iccore.data import (
    Dataset,
    DatasetPublic,
    ProductPublicWithMeasurements,
    Series,
    insert_series,
)
from iccore.data.series import filter_on_names
from iccore import filesystem as fs
from icsystemutils.network import remote

from icflow.data import csv, netcdf


logger = logging.getLogger(__name__)

_DATASET_CACHE: dict[int, Series] = {}


class BasicDataset(BaseModel, frozen=True):
    """
    This class represents a named dataset with a location,
    which can be on a remote system.
    """

    path: Path
    name: str = ""
    archive_name_override: str = ""
    hostname: str = ""

    @property
    def archive_name(self) -> str:
        if self.archive_name_override:
            return self.archive_name
        return self.name + ".zip"

    @property
    def is_readable(self) -> bool:
        return self.path.exists()


class DataRequest(BaseModel, frozen=True):

    product: ProductPublicWithMeasurements
    measurements: tuple[str, ...]
    start_datetime: datetime | None
    end_datetime: datetime | None


def _get_or_load_data(
    dataset: DatasetPublic, product: ProductPublicWithMeasurements, load_func=None
) -> Series:

    if dataset.id in _DATASET_CACHE:
        return _DATASET_CACHE[dataset.id]

    if dataset.file_format == "csv":
        _DATASET_CACHE[dataset.id] = csv.load(
            Path(dataset.original_path), dataset, product
        )
    elif dataset.file_format == "netcdf":
        _DATASET_CACHE[dataset.id] = netcdf.load(
            Path(dataset.original_path), dataset, product, load_func
        )
    return _DATASET_CACHE[dataset.id]


def load_data(req: DataRequest, load_funcs: dict | None = None) -> Series:
    """
    Loop through each sensor and dataset and load in the required quantities
    from each, returning time or time-height series.
    """

    datasets = Dataset.select_by_product(
        req.product.name, req.start_datetime, req.end_datetime
    )

    series: Series | None = None
    for d in datasets:
        load_func = load_funcs[d.name] if load_funcs else None
        s = _get_or_load_data(d, req.product, load_func)

        # Filter on measurements
        s = filter_on_names(s, list(req.measurements))

        # Shrink to dates

        if not series:
            series = s
        else:
            series = insert_series(series, s)

    if not series:
        raise RuntimeError("Requested data not found")

    return series


def archive(dataset: BasicDataset, dst: Path) -> None:
    """
    Archive the dataset in the provided location
    """
    archive_name, archive_format = dataset.archive_name.split(".")
    fs.make_archive(Path(archive_name), archive_format, dst)


def _get_archive_path(dataset: BasicDataset) -> Path:
    return dataset.path / Path(dataset.name) / Path(dataset.archive_name)


def upload(
    dataset: BasicDataset, loc: Path, upload_func: Callable | None = None
) -> None:
    """
    Upload the dataset to the given path
    """
    archive_path = _get_archive_path(dataset)
    if loc.is_dir():
        logger.info("Zipping dataset %s", dataset.archive_name)
        archive(dataset, loc)
        logger.info("Finished zipping dataset %s", dataset.archive_name)
        loc = loc / dataset.archive_name
    if dataset.hostname:
        logger.info(
            "Uploading %s to remote at %s:%s", loc, dataset.hostname, archive_path
        )

        if upload_func:
            upload_func(dataset.hostname, loc, archive_path)
        else:
            remote.upload(loc, remote.Host(name=dataset.hostname), archive_path, None)
        logger.info("Finished Uploading %s to %s", loc, archive_path)
    else:
        logger.info("Doing local copy of %s to %s", loc, archive_path)
        fs.copy(loc, archive_path)
        logger.info("Finished local copy of %s to %s", loc, archive_path)


def download(
    dataset: BasicDataset, loc: Path, download_func: Callable | None = None
) -> None:
    """
    Download the dataset from the given path
    """
    archive_path = _get_archive_path(dataset)
    if dataset.hostname:
        remote_loc = f"{dataset.hostname}:{archive_path}"
        logger.info("Downloading remote %s to %s", remote_loc, loc)
        if download_func:
            download_func(dataset.hostname, archive_path, loc)
        else:
            remote.download(remote.Host(name=dataset.hostname), archive_path, loc, None)
    else:
        logger.info("Copying %s to %s", archive_path, loc)
        fs.copy(archive_path, loc)

    archive_loc = loc / dataset.archive_name
    logger.info("Unpacking %s to %s", archive_path, loc)
    fs.unpack_archive(archive_loc, loc)
