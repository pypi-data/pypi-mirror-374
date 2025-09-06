import os

os.environ["BUGGER_OFF"] = "true"

try:
    import deeplake.client.config

    deeplake.client.config.USE_STAGING_ENVIRONMENT = True
except ImportError:
    pass #ok, no deeplake.client

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--outdated", action="store_true", default=False, help="Some tests are outdated and skipped by default."
    )
    parser.addoption(
        "--performance", action="store_true", default=False, help="Run only performance tests."
    )

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--outdated"):
        skip_outdated = pytest.mark.skip(reason="Outdated tests skipped")
        for item in items:
            if "outdated" in item.keywords:
                item.add_marker(skip_outdated)

    if not config.getoption("--performance"):
        skip_perf = pytest.mark.skip(reason="Need --performance option to run")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_perf)
    else:
        skip_non_perf = pytest.mark.skip(reason="Only performance tests running.")
        for item in items:
            if not "performance" in item.keywords:
                item.add_marker(skip_non_perf)
