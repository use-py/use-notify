import pytest

from use_notify import useNotify, useNotifyChannel


def test_from_settings():
    settings = {
        "bark": {"token": "1"}
    }
    notify = useNotify.from_settings(settings)
    assert len(notify.channels) == 1
    assert notify.channels.pop().config.token == "1"


def test_two_from_settings():
    settings = {
        "bark": {"token": "1"}
    }
    notify = useNotify.from_settings(settings)
    notify.add(useNotifyChannel.Bark({"token": "2"}))
    assert len(notify.channels) == 2


def test_unknown_from_settings():
    settings = {
        "unknown": {"token": "1"}
    }
    with pytest.raises(ValueError):
        useNotify.from_settings(settings)
