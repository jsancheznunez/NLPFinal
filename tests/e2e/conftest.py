"""Playwright config: route CDN traffic (Chart.js, Pyodide on jsDelivr) through HTTPS_PROXY if one is set;
the local static server on 127.0.0.1 is always reached directly."""
import os

import pytest


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        return {**browser_type_launch_args, "proxy": {"server": proxy, "bypass": "127.0.0.1,localhost"}}
    return browser_type_launch_args
