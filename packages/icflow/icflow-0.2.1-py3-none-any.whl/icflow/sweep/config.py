"""
This module is for a parameter sweep config file
"""

from pathlib import Path
import logging

from pydantic import BaseModel

from iccore.serialization import read_yaml
from iccore.dict_utils import merge_dicts, permute
from ictasks.session import Config

logger = logging.getLogger(__name__)


class SweepConfig(BaseModel, frozen=True):
    """
    This class handles reading a parameter sweep config file and
    also expansion of parameter ranges in lists
    """

    title: str
    program: str
    parameters: dict
    linked_parameters: dict | list[dict] | None = None
    stop_on_error: bool = False
    config: Config = Config()

    def get_expanded_params(self) -> list:
        """
        Produce a list of dictionaries from dictionaries containing list
        values.
        Each dictionary in the resultant list list is a unique permutation from
        the list entries of the original dictionaries.
        """
        # Every permutation of entries in the self.parameters dictionary are found
        items = permute(self.parameters)

        if self.linked_parameters is not None:
            if isinstance(self.linked_parameters, dict):
                linked_parameters = [self.linked_parameters]
            else:
                linked_parameters = self.linked_parameters
            for linked_set in linked_parameters:
                # All entries in the linked_parameters dictionary are lists with equal
                # lengths to one another. These lists are zipped up by their indices
                # into a list of dictionaries with the linked_parameters keys
                linked = [
                    dict(zip(linked_set.keys(), i)) for i in zip(*linked_set.values())
                ]
                items = [
                    merge_dicts(item_base, i) for i in linked for item_base in items
                ]

        return items


def read(path: Path, problem_dir: Path | None = None) -> SweepConfig:
    """
    Read the config from file
    """

    logger.info("Reading config from: %s", path)
    config = read_yaml(path)
    if problem_dir:
        config["program"] = config["program"].replace("<problem_dir>", str(problem_dir))

    return SweepConfig(**config)
