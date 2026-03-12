from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from use_notify import useNotifyChannel


def _mock_sync_http_response():
    response = MagicMock()
    response.raise_for_status = MagicMock()
    return response


def _mock_async_http_response():
    response = MagicMock()
    response.raise_for_status = MagicMock()
    return response


@patch("httpx.Client")
def test_bark_send_builds_expected_request(mock_client):
    response = _mock_sync_http_response()
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.Bark(
        {
            "token": "token",
            "base_url": "https://bark.example.com/",
            "badge": 3,
            "sound": "bell",
            "icon": None,
            "group": None,
            "url": None,
        }
    )

    channel.send("hello", "title")

    client.post.assert_called_once_with(
        "https://bark.example.com/token",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={"body": "hello", "title": "title", "badge": 3, "sound": "bell"},
    )
    response.raise_for_status.assert_called_once_with()


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_chanify_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response()
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.Chanify({"token": "token"})

    await channel.send_async("hello", "title")

    client.post.assert_awaited_once_with(
        "https://api.chanify.net/v1/sender/token",
        data={"text": "title\nhello"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status.assert_called_once_with()


def test_ding_build_api_body_includes_mentions():
    channel = useNotifyChannel.Ding(
        {
            "token": "token",
            "at_all": True,
            "at_mobiles": ["13800000000"],
            "at_user_ids": ["user-1"],
        }
    )

    body = channel.build_api_body("hello", "title")

    assert body == {
        "msgtype": "markdown",
        "markdown": {"title": "title", "text": "hello"},
        "at": {
            "isAtAll": True,
            "atMobiles": ["13800000000"],
            "atUserIds": ["user-1"],
        },
    }


def test_feishu_build_api_body_includes_mentions():
    channel = useNotifyChannel.Feishu(
        {
            "token": "token",
            "at_all": True,
            "at_user_ids": ["ou_xxx"],
        }
    )

    body = channel.build_api_body("hello", "title")
    content = body["content"]["post"]["zh_cn"]["content"][0]

    assert body["content"]["post"]["zh_cn"]["title"] == "title"
    assert {"tag": "text", "text": "hello"} in content
    assert {"tag": "at", "user_id": "all"} in content
    assert {"tag": "at", "user_id": "ou_xxx"} in content


def test_wechat_build_api_body_includes_mentions():
    channel = useNotifyChannel.WeChat(
        {
            "token": "token",
            "mentioned_list": ["@all"],
            "mentioned_mobile_list": ["13800000000"],
        }
    )

    body = channel.build_api_body("title", "hello")

    assert body == {
        "markdown": {
            "content": "## title\n\nhello",
            "mentioned_list": ["@all"],
            "mentioned_mobile_list": ["13800000000"],
        },
        "msgtype": "markdown",
    }


def test_ntfy_requires_topic_and_builds_payload():
    with pytest.raises(ValueError, match="topic"):
        useNotifyChannel.Ntfy({})

    channel = useNotifyChannel.Ntfy(
        {
            "topic": "alerts",
            "priority": 4,
            "tags": ["warning"],
            "click": "https://example.com",
        }
    )

    assert channel.api_url == "https://ntfy.sh/alerts"
    assert channel._prepare_payload("hello", "title") == {
        "message": "hello",
        "title": "title",
        "priority": 4,
        "tags": ["warning"],
        "click": "https://example.com",
    }


def test_pushdeer_prepare_params_handles_markdown_and_invalid_type(caplog):
    markdown_channel = useNotifyChannel.PushDeer({"token": "token", "type": "markdown"})
    invalid_channel = useNotifyChannel.PushDeer({"token": "token", "type": "unknown"})

    assert markdown_channel._prepare_params("hello", "title") == {
        "pushkey": "token",
        "text": "title",
        "type": "markdown",
        "desp": "hello",
    }

    caplog.clear()
    with caplog.at_level("WARNING"):
        params = invalid_channel._prepare_params("hello", "title")

    assert params["type"] == "markdown"
    assert "Invalid message type" in caplog.text


@patch("httpx.Client")
def test_pushover_send_builds_expected_request(mock_client):
    response = _mock_sync_http_response()
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.PushOver({"token": "app", "user": "user"})

    channel.send("hello", "title")

    client.post.assert_called_once_with(
        "https://api.pushover.net/1/messages.json",
        data={"token": "app", "user": "user", "title": "title", "message": "hello"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status.assert_called_once_with()


def test_console_send_outputs_message(capsys):
    channel = useNotifyChannel.Console()

    channel.send("hello", "title")

    output = capsys.readouterr().out
    assert "title" in output
    assert "hello" in output
