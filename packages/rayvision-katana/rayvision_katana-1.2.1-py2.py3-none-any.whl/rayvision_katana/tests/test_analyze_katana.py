"""Test for analyze_katana_handle.py."""

# pylint: disable=import-error
import pytest

from rayvision_utils.exception.exception import CGFileNotExistsError


def test_check_path(katana_analyze):
    """Test init this interface.

    Test We can get an ``FileNameContainsChineseError`` if the information is
    wrong.

    """
    katana_analyze.cg_file = "xxx.katana"
    with pytest.raises(CGFileNotExistsError):
        katana_analyze.check_path(katana_analyze.cg_file)

