#!/usr/bin/env python3

import shutil

from iccore.test_utils import get_test_data_dir, get_test_output_dir
from iccore.serialization import read_yaml
import ictasks.task
from ictasks.task import Task

import icflow
import icflow.sweep
import icflow.sweep.reporter as reporter


def test_parameter_sweep():
    work_dir = get_test_output_dir()
    data_dir = get_test_data_dir()

    config_path = data_dir / "parameter_sweep_example.yaml"

    sweep_dir = icflow.sweep.run(
        icflow.sweep.config.read(config_path, problem_dir=data_dir),
        work_dir,
        config_path,
    )
    result_dir = sweep_dir / "tasks"

    tasks = ictasks.task.read_all(result_dir)
    for task in tasks:
        assert task.finished and task.return_code == 0
    assert len(tasks) == 4

    reporter.cpu_monitor_plot(sweep_dir)

    shutil.rmtree(work_dir)


def test_linked_parameter_sweep():
    work_dir = get_test_output_dir()
    data_dir = get_test_data_dir()

    config_path = data_dir / "linked_parameter_sweep_example.yaml"

    sweep_dir = icflow.sweep.run(
        icflow.sweep.config.read(config_path, problem_dir=data_dir),
        work_dir,
        config_path,
    )
    result_dir = sweep_dir / "tasks"

    tasks = ictasks.task.read_all(result_dir)
    for task in tasks:
        assert task.finished and task.return_code == 0
    assert len(tasks) == 4

    shutil.rmtree(work_dir)


def test_parameter_sweep_reporter():

    tasks = [
        Task(
            id="complete_task",
            launch_cmd="python3 fake.py --complete",
            state="finished",
            pid=21,
        ),
        Task(
            id="incomplete_task",
            launch_cmd="python3 fake.py --incomplete",
            state="created",
            pid=22,
        ),
    ]

    task_str = ictasks.task.tasks_to_str(
        [t for t in tasks if t.finished], ["id", "launch_cmd", "pid"]
    )

    assert "id: complete_task" in task_str
    assert "id: incomplete_task" not in task_str
    assert "launch_cmd: python3 fake.py --complete" in task_str
    assert "launch_cmd: python3 fake.py --incomplete" not in task_str
    assert "pid: 21" in task_str
    assert "pid: 22" not in task_str


def test_subsets():
    tasks = [
        Task(
            id="1",
            launch_cmd="python3 fake.py --parameter_1 3 --parameter_2 1 --parameter_3 1",
        ),
        Task(
            id="2",
            launch_cmd="python3 fake.py --parameter_1 1",
        ),
        Task(
            id="3",
            launch_cmd="python3 fake.py --parameter_2 2",
        ),
        Task(
            id="4",
            launch_cmd="python3 fake.py --parameter_3 8",
        ),
    ]

    data_dir = get_test_data_dir()

    config = read_yaml(data_dir / "sweep_subset_example.yaml")

    tasks = reporter.filter_tasks_with_config(
        tasks, config, reporter.task_params_in_range
    )
    assert len(tasks) == 1
