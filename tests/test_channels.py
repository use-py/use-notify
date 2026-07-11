from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from use_notify import useNotifyChannel
from use_notify.channels.utils import ProviderResponseError, validate_business_response


def _mock_sync_http_response(json_data=None):
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.side_effect = ValueError("response body is not JSON")
    return response


def _mock_async_http_response(json_data=None):
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if json_data is not None:
        response.json.return_value = json_data
    else:
        response.json.side_effect = ValueError("response body is not JSON")
    return response


def _credential_provider(*values):
    values_iter = iter(values)
    return lambda: next(values_iter)


def test_validate_business_response_ignores_non_dict_json_payloads():
    response = _mock_sync_http_response(["ok"])

    validate_business_response(response, "provider", {"code": {0}})


def test_validate_business_response_serializes_dict_error_detail():
    response = _mock_sync_http_response({"code": 1, "error": {"reason": "bad token"}})

    with pytest.raises(ProviderResponseError) as error_info:
        validate_business_response(response, "provider", {"code": {0}})

    assert '"reason": "bad token"' in str(error_info.value)


def test_validate_business_response_falls_back_to_payload_detail():
    response = _mock_sync_http_response({"code": 1, "detail": "bad token"})

    with pytest.raises(ProviderResponseError) as error_info:
        validate_business_response(response, "provider", {"code": {0}})

    assert '"code": 1' in str(error_info.value)
    assert '"detail": "bad token"' in str(error_info.value)


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


def test_bark_minimal_config_omits_missing_optional_fields():
    channel = useNotifyChannel.Bark({"token": "token"})

    assert channel._prepare_payload("hello", "title") == {
        "body": "hello",
        "title": "title",
    }


def test_bark_preserves_explicit_falsy_optional_values():
    channel = useNotifyChannel.Bark({"token": "token", "badge": 0})

    assert channel._prepare_payload("hello") == {
        "body": "hello",
        "badge": 0,
    }


def test_bark_resolves_callable_token_each_time():
    channel = useNotifyChannel.Bark({"token": _credential_provider("first", "second")})

    assert channel.api_url == "https://api.day.app/first"
    assert channel.api_url == "https://api.day.app/second"


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


@patch("httpx.Client")
def test_chanify_send_builds_expected_request(mock_client):
    response = _mock_sync_http_response({"res": 0})
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.Chanify(
        {
            "token": "token",
            "base_url": "https://chanify.example.com/",
        }
    )

    channel.send("hello", "title")

    client.post.assert_called_once_with(
        "https://chanify.example.com/v1/sender/token",
        data={"text": "title\nhello"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status.assert_called_once_with()


def test_chanify_omits_title_when_missing():
    channel = useNotifyChannel.Chanify({"token": "token"})

    assert channel.build_api_body("hello") == {"text": "hello"}


def test_chanify_resolves_callable_token_each_time():
    channel = useNotifyChannel.Chanify({"token": _credential_provider("first", "second")})

    assert channel.api_url == "https://api.chanify.net/v1/sender/first"
    assert channel.api_url == "https://api.chanify.net/v1/sender/second"


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


def test_ding_resolves_callable_token_each_time():
    channel = useNotifyChannel.Ding({"token": _credential_provider("first", "second")})

    assert channel.api_url == "https://oapi.dingtalk.com/robot/send?access_token=first"
    assert channel.api_url == "https://oapi.dingtalk.com/robot/send?access_token=second"


@patch("httpx.Client")
def test_ding_send_rejects_business_error_response(mock_client):
    response = _mock_sync_http_response({"errcode": 310000, "errmsg": "invalid token"})
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.Ding({"token": "token"})

    with pytest.raises(RuntimeError, match="ding.*invalid token"):
        channel.send("hello", "title")


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_ding_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response({"errcode": 0})
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.Ding({"token": "token"})

    await channel.send_async("hello", "title")

    client.post.assert_awaited_once_with(
        "https://oapi.dingtalk.com/robot/send?access_token=token",
        json={"msgtype": "markdown", "markdown": {"title": "title", "text": "hello"}, "at": {}},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status.assert_called_once_with()


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


def test_feishu_resolves_callable_token_each_time():
    channel = useNotifyChannel.Feishu({"token": _credential_provider("first", "second")})

    assert channel.api_url == "https://open.feishu.cn/open-apis/bot/v2/hook/first"
    assert channel.api_url == "https://open.feishu.cn/open-apis/bot/v2/hook/second"


@patch("httpx.Client")
def test_feishu_send_rejects_business_error_response(mock_client):
    response = _mock_sync_http_response({"code": 9499, "msg": "bad webhook"})
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.Feishu({"token": "token"})

    with pytest.raises(RuntimeError, match="feishu.*bad webhook"):
        channel.send("hello", "title")


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_feishu_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response({"code": 0})
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.Feishu({"token": "token"})

    await channel.send_async("hello", "title")

    client.post.assert_awaited_once_with(
        "https://open.feishu.cn/open-apis/bot/v2/hook/token",
        json={
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "title",
                        "content": [[{"tag": "text", "text": "hello"}]],
                    }
                }
            },
        },
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status.assert_called_once_with()


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


def test_wechat_resolves_callable_token_each_time():
    channel = useNotifyChannel.WeChat({"token": _credential_provider("first", "second")})

    assert channel.api_url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=first"
    assert channel.api_url == "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=second"


def test_wechat_omits_title_when_missing():
    channel = useNotifyChannel.WeChat({"token": "token"})

    assert channel.build_api_body(None, "hello") == {
        "markdown": {"content": "hello"},
        "msgtype": "markdown",
    }


@patch("httpx.Client")
def test_wechat_send_rejects_business_error_response(mock_client):
    response = _mock_sync_http_response({"errcode": 40001, "errmsg": "invalid credential"})
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.WeChat({"token": "token"})

    with pytest.raises(RuntimeError, match="wechat.*invalid credential"):
        channel.send("hello", "title")


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_wechat_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response({"errcode": 0})
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.WeChat({"token": "token"})

    await channel.send_async("hello", "title")

    client.post.assert_awaited_once_with(
        "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=token",
        json={"markdown": {"content": "## title\n\nhello"}, "msgtype": "markdown"},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status.assert_called_once_with()


def test_ntfy_requires_topic_and_builds_payload():
    with pytest.raises(ValueError, match="topic"):
        useNotifyChannel.Ntfy({})

    minimal_channel = useNotifyChannel.Ntfy({"topic": "alerts"})
    assert minimal_channel.api_url == "https://ntfy.sh/alerts"
    assert minimal_channel._prepare_payload("hello", "title") == {
        "message": "hello",
        "title": "title",
    }

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


def test_ntfy_resolves_callable_topic_each_time():
    channel = useNotifyChannel.Ntfy({"topic": _credential_provider("first", "second")})

    assert channel.api_url == "https://ntfy.sh/first"
    assert channel.api_url == "https://ntfy.sh/second"


@patch("httpx.Client")
def test_ntfy_send_builds_expected_request(mock_client):
    response = _mock_sync_http_response()
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.Ntfy(
        {
            "topic": "alerts",
            "base_url": "https://ntfy.example.com/",
            "attach": "https://example.com/file.txt",
            "actions": [{"action": "view", "label": "Open", "url": "https://example.com"}],
        }
    )

    channel.send("hello", "title")

    client.post.assert_called_once_with(
        "https://ntfy.example.com/alerts",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={
            "message": "hello",
            "title": "title",
            "attach": "https://example.com/file.txt",
            "actions": [{"action": "view", "label": "Open", "url": "https://example.com"}],
        },
    )
    response.raise_for_status.assert_called_once_with()


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_ntfy_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response()
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.Ntfy({"topic": "alerts"})

    await channel.send_async("hello")

    client.post.assert_awaited_once_with(
        "https://ntfy.sh/alerts",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={"message": "hello"},
    )
    response.raise_for_status.assert_called_once_with()


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


def test_pushdeer_requires_token_for_api_url():
    channel = useNotifyChannel.PushDeer({})

    with pytest.raises(ValueError, match="pushkey"):
        _ = channel.api_url


def test_pushdeer_resolves_callable_token_each_time():
    channel = useNotifyChannel.PushDeer({"token": _credential_provider("first", "second")})

    assert channel._prepare_params("hello")["pushkey"] == "first"
    assert channel._prepare_params("hello")["pushkey"] == "second"


def test_pushdeer_api_url_uses_custom_base_url():
    channel = useNotifyChannel.PushDeer(
        {
            "token": "token",
            "base_url": "https://pushdeer.example.com/",
        }
    )

    assert channel.api_url == "https://pushdeer.example.com/message/push"


def test_pushdeer_prepare_params_handles_default_title_text_and_image():
    default_channel = useNotifyChannel.PushDeer({"token": "token"})
    text_channel = useNotifyChannel.PushDeer({"token": "token", "type": "text"})
    image_channel = useNotifyChannel.PushDeer({"token": "token", "type": "image"})

    assert default_channel._prepare_params("hello") == {
        "pushkey": "token",
        "text": "消息提醒",
        "type": "markdown",
        "desp": "hello",
    }
    assert text_channel._prepare_params("hello", "title") == {
        "pushkey": "token",
        "text": "hello",
        "type": "text",
    }
    assert image_channel._prepare_params("https://example.com/image.png", "title") == {
        "pushkey": "token",
        "text": "title",
        "type": "image",
        "desp": "https://example.com/image.png",
    }


@patch("httpx.Client")
def test_pushdeer_send_builds_expected_request(mock_client):
    response = _mock_sync_http_response({"code": 0})
    client = mock_client.return_value.__enter__.return_value
    client.get.return_value = response
    channel = useNotifyChannel.PushDeer({"token": "token", "type": "text"})

    channel.send("hello", "title")

    client.get.assert_called_once_with(
        "https://api2.pushdeer.com/message/push",
        params={"pushkey": "token", "text": "hello", "type": "text"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status.assert_called_once_with()


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_pushdeer_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response({"code": 0})
    client = mock_client.return_value.__aenter__.return_value
    client.get = AsyncMock(return_value=response)
    channel = useNotifyChannel.PushDeer({"token": "token"})

    await channel.send_async("hello", "title")

    client.get.assert_awaited_once_with(
        "https://api2.pushdeer.com/message/push",
        params={"pushkey": "token", "text": "title", "type": "markdown", "desp": "hello"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status.assert_called_once_with()


@patch("httpx.Client")
def test_pushdeer_send_rejects_business_error_response(mock_client):
    response = _mock_sync_http_response({"code": 80403, "error": "pushkey invalid"})
    client = mock_client.return_value.__enter__.return_value
    client.get.return_value = response
    channel = useNotifyChannel.PushDeer({"token": "token"})

    with pytest.raises(RuntimeError, match="pushdeer.*pushkey invalid"):
        channel.send("hello", "title")


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


def test_pushover_resolves_callable_credentials_each_time():
    channel = useNotifyChannel.PushOver(
        {
            "token": _credential_provider("app-1", "app-2"),
            "user": _credential_provider("user-1", "user-2"),
        }
    )

    first_payload = channel.build_api_body("hello")
    second_payload = channel.build_api_body("hello")

    assert first_payload["token"] == "app-1"
    assert first_payload["user"] == "user-1"
    assert second_payload["token"] == "app-2"
    assert second_payload["user"] == "user-2"


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_pushover_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response({"status": 1})
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.PushOver({"token": "app", "user": "user"})

    await channel.send_async("hello", "title")

    client.post.assert_awaited_once_with(
        "https://api.pushover.net/1/messages.json",
        data={"token": "app", "user": "user", "title": "title", "message": "hello"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    response.raise_for_status.assert_called_once_with()


@patch("httpx.Client")
def test_pushover_send_rejects_business_error_response(mock_client):
    response = _mock_sync_http_response({"status": 0, "errors": ["bad user"]})
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.PushOver({"token": "app", "user": "user"})

    with pytest.raises(RuntimeError, match="pushover.*bad user"):
        channel.send("hello", "title")


@patch("httpx.Client")
def test_bark_send_rejects_business_error_response(mock_client):
    response = _mock_sync_http_response({"code": 400, "message": "bad device token"})
    client = mock_client.return_value.__enter__.return_value
    client.post.return_value = response
    channel = useNotifyChannel.Bark({"token": "token"})

    with pytest.raises(RuntimeError, match="bark.*bad device token"):
        channel.send("hello", "title")


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_bark_send_async_builds_expected_request(mock_client):
    response = _mock_async_http_response({"code": 200})
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.Bark({"token": "token"})

    await channel.send_async("hello")

    client.post.assert_awaited_once_with(
        "https://api.day.app/token",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={"body": "hello"},
    )
    response.raise_for_status.assert_called_once_with()


@patch("httpx.AsyncClient")
@pytest.mark.asyncio
async def test_chanify_send_async_rejects_business_error_response(mock_client):
    response = _mock_async_http_response({"res": 1, "msg": "invalid token"})
    client = mock_client.return_value.__aenter__.return_value
    client.post = AsyncMock(return_value=response)
    channel = useNotifyChannel.Chanify({"token": "token"})

    with pytest.raises(RuntimeError, match="chanify.*invalid token"):
        await channel.send_async("hello", "title")


def test_console_send_outputs_message(capsys):
    channel = useNotifyChannel.Console()

    channel.send("hello", "title")

    output = capsys.readouterr().out
    assert "title" in output
    assert "hello" in output


@pytest.mark.asyncio
async def test_console_send_async_outputs_message(capsys):
    channel = useNotifyChannel.Console()

    await channel.send_async("hello", "title")

    output = capsys.readouterr().out
    assert "title" in output
    assert "hello" in output
