import pytest

from fileforge.modules.settings import get_all_settings, get_setting, set_setting


def test_settings_read_write():
    set_setting("theme", "deep-space")
    assert get_setting("theme") == "deep-space"

    set_setting("max_tree_depth", "6")
    assert get_setting("max_tree_depth") == "6"

    all_s = get_all_settings()
    assert all_s["max_tree_depth"] == "6"


def test_protected_settings_cannot_be_disabled():
    with pytest.raises(ValueError, match="cannot be disabled"):
        set_setting("require_confirmation", "false")
