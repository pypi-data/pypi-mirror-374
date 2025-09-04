"""
Handle data loading from csv files
"""

import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

from iccore.data import DatasetCreate, DatasetPublic, ProductPublicWithMeasurements
from iccore.data.series import Array, Series


logger = logging.getLogger(__name__)


def gettype(name):

    if name == "str":
        return str
    raise ValueError(name)


def load(
    path: Path,
    dataset: DatasetCreate | DatasetPublic,
    product: ProductPublicWithMeasurements,
) -> Series:
    """
    Load the requested quantities from the provided path.

    Return a dict keyed on quantity labels, with values as a tuple of
    the Quantity type and the corresponding pandas dataframe.
    """

    logger.info("Loading data from %s.", path)

    dtypes = {k: gettype(v) for k, v in dataset.type_specs.items()}

    # dates are in column =dataset.time_column in datestring format, automatically
    # parse them and use them as an index
    data = pd.read_csv(path, parse_dates=True, dtype=dtypes)

    fields = {m.name: m.name for m in product.measurements}
    for m, column in dataset.fields.items():
        fields[m] = column

    values = []
    for m, c in fields.items():

        if m == "time":
            values.append(
                Array(name=m, data=[datetime.fromisoformat(d) for d in data[c]])
            )
        else:
            values.append(Array(name=m, data=data[c]))

    return Series(values=values, x=product.x.name if product.x else None)
