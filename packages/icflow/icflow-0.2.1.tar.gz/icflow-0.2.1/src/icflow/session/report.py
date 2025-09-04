"""
Module representing a computational workflow
"""

from pathlib import Path
import logging

from pydantic import BaseModel

from iccore.data import (
    Product,
    ProductPublicWithMeasurements,
)
from iccore.serialization import yaml_utils

from icplot.graph import (
    PlotGroupCreate,
    PlotGroupPublic,
    PlotSeriesPublic,
    plot_series,
)

from icflow.data.dataset import DataRequest, load_data


logger = logging.getLogger(__name__)


class Report(BaseModel, frozen=True):
    """
    A computational or data-processing workflow

    :cvar name: A name or label
    :cvar plots: Description of plots to generate
    """

    name: str
    plots: list[PlotGroupCreate] = []


def load_report(path: Path) -> Report:
    report_yaml = yaml_utils.read_yaml(path)
    return Report(**report_yaml)


def generate(report: Report, output_dir: Path, load_funcs: dict | None = None):

    logger.info("Generating report: %s", report.name)

    logger.info("Generating plots")

    for plot_group in report.plots:
        if not plot_group.active:
            continue

        # populate plot series
        for s in plot_group.series:

            logger.info("Plotting %s", s.measurement)

            product = Product.object(
                s.product, "name", return_t=ProductPublicWithMeasurements
            )

            logger.info("Reading data")

            data_series = load_data(
                DataRequest(
                    product=product,
                    measurements=(s.base_measurement,),
                    start_datetime=plot_group.start_datetime,
                    end_datetime=plot_group.end_datetime,
                ),
                load_funcs,
            )

            logger.info("Finished Reading data")

            logger.info("Generating plot")

            series_dump = plot_group.model_dump()
            series_dump["series"] = []

            plot_series(
                output_dir / report.name,
                PlotGroupPublic.model_validate(series_dump),
                PlotSeriesPublic.from_create(s, product),
                data_series,
            )

    logger.info("Finished generating plots")


def report_generate(path: Path, output_dir: Path, load_funcs: dict | None = None):

    generate(load_report(path), output_dir, load_funcs)
