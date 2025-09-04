`icflow` is a Python package with some prototype workflow tools for use at the Irish Centre for High End Computing (ICHEC).

It is intended to help standardize some of our workflows in areas like Machine Learning by using common utilities, data-formats and data-structures. 

See the project documentation on [ReadTheDocs](https://icflow.readthedocs.io/en/latest/).

# Features #

## Parameter Sweep ##

You can define a parameter sweep in a `yaml` file as follows:

``` yaml
title: "my_parameter_sweep"
program: "launch_program"  

parameters:
    param_0 : 1
    param_1 : "my_value"
    param_2 : [1, 2]
    param_3 : ["a", "b"]
```

Running:

``` shell
icflow sweep --config my_config.yaml
```

with this fill will launch the program or script defined by `program`, which should be in the system `PATH`.

The listed parameters are passed as command line arguments to the `program` in the form `--key value`. Parameter value lists are expanded such that there is a program launch for each combination of values in the list. In the above example this will result in the following program launches:

``` shell
launch_program --param_0 1 --param_1 my_value --param_2 1 --param_3 a
launch_program --param_0 1 --param_1 my_value --param_2 2 --param_3 a
launch_program --param_0 1 --param_1 my_value --param_2 1 --param_3 b
launch_program --param_0 1 --param_1 my_value --param_2 2 --param_3 b
```

Program launching is handled internally by ICHEC's [ictasks](https://git.ichec.ie/performance/toolshed/ictasks) library, with each of these program launches handled as a 'task'.


### Running sweeps in parallel ###
You can also specify details about the number of gpu/cpu s available for running tasks by including the `config` and inner `task_distribution` sections in the sweep config This can allow for tasks to be run in parallel, see a description in [ictasks](https://git.ichec.ie/performance/toolshed/ictasks) covering this `task_distribution` and using gpus in your tasks.

``` yaml
title: ...
program: ... 

parameters:
    ...

config:
    task_distribution:
        ...
```

# Installation #

It is available on PyPI:

``` shell
pip install icflow
```

# Copyright

This software is Copyright of the Irish Centre for High End Computing 2024. You can use it under the terms of the GPLv3+. See the included `LICENSE` file for details.
