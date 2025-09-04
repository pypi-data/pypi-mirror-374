"""
This module has functionality to support running in
a distributed context
"""

import platform
from pathlib import Path

from iccore.serialization import write_model
from iccore.system.environment import Environment
from icsystemutils.network import info
from icsystemutils.cpu import process, cpu_info


def load(local_rank: int = 0) -> Environment:
    return Environment(
        process=process.load(local_rank),
        network=info.load(),
        cpu_info=cpu_info.read(),
        platform=platform.platform(),
    )


def write(env: Environment, path: Path, filename: str = "environment.json") -> None:
    write_model(env, path / filename)
