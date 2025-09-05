import os

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return

    skip_slow = pytest.mark.skip(reason="need --runslow option to run")

    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_itemcollected(item):
    """we just collected a test item."""
    if any("slow" in name for name in item.fixturenames):
        item.add_marker("slow")


@pytest.fixture
def runs_on_ci_server():
    # CI is set by gitlab-ci server
    return os.environ.get("CI") is not None
