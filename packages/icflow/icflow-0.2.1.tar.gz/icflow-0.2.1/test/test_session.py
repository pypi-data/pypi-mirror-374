from iccore.test_utils import get_test_output_dir

from icflow.session import App
from icflow import environment


def test_session():

    work_dir = get_test_output_dir()

    env = environment.load()

    _ = App(env, None, work_dir)
