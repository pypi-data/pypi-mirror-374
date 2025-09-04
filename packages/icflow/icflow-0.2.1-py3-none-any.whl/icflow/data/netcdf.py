from pathlib import Path
import logging
import gzip

import numpy as np
from netCDF4 import Dataset

from iccore.data.units import to_timestamps
from iccore.data import (
    DatasetCreate,
    DatasetPublic,
    ProductPublicWithMeasurements,
    Series,
    Array,
)

logger = logging.getLogger(__name__)

_TIME_REF = "2001-01-01T00:00:00Z"


# TODO - fix arg types in iccore and use those interfaces instead


def is_file_with_extensions(
    f, extensions: tuple[str, ...], excludes: list[str] | None = None
):
    """
    True if the path item is a file and has one of the provided extensions
    """

    if not f.is_file():
        return False
    for ext in extensions:
        check_str = str(f).lower()
        if check_str.endswith(f".{ext.lower()}"):
            if excludes:
                for exclude in excludes:
                    if check_str.endswith(f"{exclude.lower()}.{ext.lower()}"):
                        return False
            return True
    return False


def get_files_recursive(
    path: Path, extensions: tuple[str, ...], excludes: list[str] | None = None
):
    """
    Get all provided files recursively, filter on extensions and excludes
    """
    return [
        f for f in path.rglob("*") if is_file_with_extensions(f, extensions, excludes)
    ]


def _load_nc(
    nc, dataset: DatasetCreate, product: ProductPublicWithMeasurements
) -> Series:

    if not product.x or not product.y:
        raise RuntimeError("Product expected to have x and y values.")

    fields = {m.name: m.name for m in product.measurements}
    for m, v in dataset.fields.items():
        fields[m] = v

    values = []
    for m, v in fields.items():
        data = nc.variables[v][:]
        if m == "time":
            data = np.array(to_timestamps(data, _TIME_REF))
        values.append(Array(name=m, data=data))

    return Series(x=product.x.name, y=product.y.name, values=values)


def load(
    path: Path,
    dataset: DatasetCreate | DatasetPublic,
    product: ProductPublicWithMeasurements,
    load_func,
) -> Series:

    if load_func is None:
        load_func = _load_nc

    logger.info("Reading data from %s", path)

    if str(path).endswith(".gz"):
        with gzip.open(path) as gz:
            with Dataset("dummy", mode="r", memory=gz.read()) as nc:
                if dataset.group_prefix:
                    for name, group in nc.groups.items():
                        if name.startswith(dataset.group_prefix):
                            return load_func(group, dataset, product)
                    raise RuntimeError("No group found in netcdf archive")
                return load_func(nc, dataset, product)

    else:
        with Dataset(path, mode="r") as nc:
            if dataset.group_prefix:
                for name, group in nc.groups.items():
                    if name.startswith(dataset.group_prefix):
                        return load_func(group, dataset, product)
                raise RuntimeError("No group found in netcdf archive")
            return load_func(nc, dataset, product)
