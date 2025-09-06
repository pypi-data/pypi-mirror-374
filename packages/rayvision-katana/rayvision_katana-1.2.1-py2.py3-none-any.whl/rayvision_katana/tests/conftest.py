"""The plugin of the pytest.

The pytest plugin hooks do not need to be imported into any test code, it will
load automatically when running pytest.

References:
    https://docs.pytest.org/en/2.7.3/plugins.html

"""

# pylint: disable=import-error
import pytest

from rayvision_katana.analyse_katana import AnalyzeKatana


@pytest.fixture()
def analyze_info(tmpdir):
    """Get user info."""
    cg_file = str(tmpdir.join('arnold_test.katana'))
    with open(cg_file, "w"):
        pass
    return {
    "cg_file": cg_file,
    "workspace": str(tmpdir),
    "software_version": "3.2v1",
    "project_name": "Project1",
    "plugin_config": {
        "KtoA": "2.4.0.3"
    }
}


@pytest.fixture()
def katana_analyze(analyze_info):
    """Create an katana object."""
    return AnalyzeKatana(**analyze_info)
