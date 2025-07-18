import pytest
from unittest.mock import patch, MagicMock

from use_notify.channels.ntfy import Ntfy


test_topic = "my-notifications-test-topic"


@pytest.fixture
def ntfy_config():
    return {
        "topic": test_topic,
        "priority": 3,
        "tags": ["warning", "skull"],
        "click": "https://example.com",
        "attach": "https://example.com/file.jpg",
    }


@pytest.fixture
def minimal_ntfy_config():
    return {"topic": test_topic}


@pytest.fixture
def custom_server_config():
    return {"topic": test_topic, "base_url": "https://ntfy.example.com"}


def test_ntfy_init_with_minimal_config(minimal_ntfy_config):
    """测试使用最小配置初始化 Ntfy"""
    ntfy = Ntfy(minimal_ntfy_config)
    assert ntfy.config.topic == test_topic


def test_ntfy_init_with_full_config(ntfy_config):
    """测试使用完整配置初始化 Ntfy"""
    ntfy = Ntfy(ntfy_config)
    assert ntfy.config.topic == test_topic
    assert ntfy.config.priority == 3
    assert ntfy.config.tags == ["warning", "skull"]
    assert ntfy.config.click == "https://example.com"
    assert ntfy.config.attach == "https://example.com/file.jpg"


def test_ntfy_init_without_topic():
    """测试没有 topic 时应该抛出异常"""
    with pytest.raises(ValueError, match="Ntfy channel requires 'topic' in config"):
        Ntfy({})


def test_ntfy_init_with_empty_topic():
    """测试空 topic 时应该抛出异常"""
    with pytest.raises(ValueError, match="Ntfy channel requires 'topic' in config"):
        Ntfy({"topic": ""})


def test_api_url_construction_default(minimal_ntfy_config):
    """测试默认 API URL 构建"""
    ntfy = Ntfy(minimal_ntfy_config)
    assert ntfy.api_url == f"https://ntfy.sh/{test_topic}"


def test_api_url_construction_custom(custom_server_config):
    """测试自定义服务器 API URL 构建"""
    ntfy = Ntfy(custom_server_config)
    assert ntfy.api_url == f"https://ntfy.example.com/{test_topic}"


def test_api_url_with_trailing_slash():
    """测试带尾随斜杠的 base_url 规范化"""
    config = {"topic": test_topic, "base_url": "https://ntfy.example.com/"}
    ntfy = Ntfy(config)
    assert ntfy.api_url == f"https://ntfy.example.com/{test_topic}"


def test_headers():
    """测试请求头"""
    ntfy = Ntfy({"topic": test_topic})
    headers = ntfy.headers
    assert headers["Content-Type"] == "application/json; charset=utf-8"


def test_prepare_payload_minimal():
    """测试最小负载准备"""
    ntfy = Ntfy({"topic": test_topic})
    payload = ntfy._prepare_payload("Test message")

    assert payload["message"] == "Test message"
    assert "title" not in payload


def test_prepare_payload_with_title():
    """测试带标题的负载准备"""
    ntfy = Ntfy({"topic": test_topic})
    payload = ntfy._prepare_payload("Test message", "Test title")

    assert payload["message"] == "Test message"
    assert payload["title"] == "Test title"


def test_prepare_payload_with_advanced_features(ntfy_config):
    """测试带高级功能的负载准备"""
    ntfy = Ntfy(ntfy_config)
    payload = ntfy._prepare_payload("Test message", "Test title")

    assert payload["message"] == "Test message"
    assert payload["title"] == "Test title"
    assert payload["priority"] == 3
    assert payload["tags"] == ["warning", "skull"]
    assert payload["click"] == "https://example.com"
    assert payload["attach"] == "https://example.com/file.jpg"


def test_prepare_payload_with_actions():
    """测试带操作的负载准备"""
    config = {
        "topic": test_topic,
        "actions": [
            {"action": "view", "label": "Open portal", "url": "https://home.nest.com/"}
        ],
    }
    ntfy = Ntfy(config)
    payload = ntfy._prepare_payload("Test message")

    assert payload["actions"] == config["actions"]


def test_send_success(minimal_ntfy_config):
    """测试同步发送成功"""
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    # Create Ntfy instance
    ntfy = Ntfy(minimal_ntfy_config)

    # Mock the httpx.Client
    with patch("httpx.Client", mock_client):
        ntfy.send("Test message", "Test title")

    # Verify the request was made correctly
    mock_client.return_value.__enter__.return_value.post.assert_called_once()

    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]

    # Verify URL and headers
    assert url == f"https://ntfy.sh/{test_topic}"
    assert kwargs["headers"]["Content-Type"] == "application/json; charset=utf-8"

    # Verify payload
    payload = kwargs["json"]
    assert payload["message"] == "Test message"
    assert payload["title"] == "Test title"

    # Verify response handling
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_send_async_success(minimal_ntfy_config):
    """测试异步发送成功"""
    # Create a mock for httpx.AsyncClient
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

    # Create Ntfy instance
    ntfy = Ntfy(minimal_ntfy_config)

    # Mock the httpx.AsyncClient
    with patch("httpx.AsyncClient", mock_client):
        await ntfy.send_async("Test message", "Test title")

    # Verify the request was made correctly
    mock_client.return_value.__aenter__.return_value.post.assert_called_once()

    # Get the call arguments
    call_args = mock_client.return_value.__aenter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]

    # Verify URL and headers
    assert url == f"https://ntfy.sh/{test_topic}"
    assert kwargs["headers"]["Content-Type"] == "application/json; charset=utf-8"

    # Verify payload
    payload = kwargs["json"]
    assert payload["message"] == "Test message"
    assert payload["title"] == "Test title"

    # Verify response handling
    mock_response.raise_for_status.assert_called_once()


def test_send_with_advanced_features(ntfy_config):
    """测试带高级功能的同步发送"""
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    # Create Ntfy instance
    ntfy = Ntfy(ntfy_config)

    # Mock the httpx.Client
    with patch("httpx.Client", mock_client):
        ntfy.send("Test message", "Test title")

    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    kwargs = call_args[1]

    # Verify payload includes advanced features
    payload = kwargs["json"]
    assert payload["message"] == "Test message"
    assert payload["title"] == "Test title"
    assert payload["priority"] == 3
    assert payload["tags"] == ["warning", "skull"]
    assert payload["click"] == "https://example.com"
    assert payload["attach"] == "https://example.com/file.jpg"


def test_send_http_error(minimal_ntfy_config):
    """测试 HTTP 错误处理"""
    import httpx

    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=MagicMock()
    )
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    # Create Ntfy instance
    ntfy = Ntfy(minimal_ntfy_config)

    # Mock the httpx.Client and expect exception
    with patch("httpx.Client", mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            ntfy.send("Test message")


@pytest.mark.asyncio
async def test_send_async_http_error(minimal_ntfy_config):
    """测试异步 HTTP 错误处理"""
    import httpx

    # Create a mock for httpx.AsyncClient
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", request=MagicMock(), response=MagicMock()
    )
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

    # Create Ntfy instance
    ntfy = Ntfy(minimal_ntfy_config)

    # Mock the httpx.AsyncClient and expect exception
    with patch("httpx.AsyncClient", mock_client):
        with pytest.raises(httpx.HTTPStatusError):
            await ntfy.send_async("Test message")


def test_send_request_error(minimal_ntfy_config):
    """测试网络请求错误处理"""
    import httpx

    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_client.return_value.__enter__.return_value.post.side_effect = (
        httpx.RequestError("Connection failed")
    )

    # Create Ntfy instance
    ntfy = Ntfy(minimal_ntfy_config)

    # Mock the httpx.Client and expect exception
    with patch("httpx.Client", mock_client):
        with pytest.raises(httpx.RequestError):
            ntfy.send("Test message")


@pytest.mark.asyncio
async def test_send_async_request_error(minimal_ntfy_config):
    """测试异步网络请求错误处理"""
    import httpx

    # Create a mock for httpx.AsyncClient
    mock_client = MagicMock()
    mock_client.return_value.__aenter__.return_value.post.side_effect = (
        httpx.RequestError("Connection failed")
    )

    # Create Ntfy instance
    ntfy = Ntfy(minimal_ntfy_config)

    # Mock the httpx.AsyncClient and expect exception
    with patch("httpx.AsyncClient", mock_client):
        with pytest.raises(httpx.RequestError):
            await ntfy.send_async("Test message")


def test_integration_with_publisher():
    """测试与 Publisher 的集成"""
    from use_notify.notification import Publisher

    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    # Create Ntfy instance and Publisher
    ntfy = Ntfy({"topic": test_topic})
    publisher = Publisher()
    publisher.add(ntfy)

    # Mock the httpx.Client
    with patch("httpx.Client", mock_client):
        publisher.publish("Test message", "Test title")

    # Verify the request was made
    mock_client.return_value.__enter__.return_value.post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_integration_with_publisher_async():
    """测试与 Publisher 的异步集成"""
    from use_notify.notification import Publisher

    # Create a mock for httpx.AsyncClient
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

    # Create Ntfy instance and Publisher
    ntfy = Ntfy({"topic": test_topic})
    publisher = Publisher()
    publisher.add(ntfy)

    # Mock the httpx.AsyncClient
    with patch("httpx.AsyncClient", mock_client):
        await publisher.publish_async("Test message", "Test title")

    # Verify the request was made
    mock_client.return_value.__aenter__.return_value.post.assert_called_once()
    mock_response.raise_for_status.assert_called_once()


def test_integration_with_notify_from_settings():
    """测试与 Notify.from_settings() 的集成"""
    from use_notify.notification import Notify

    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    # Create settings
    settings = {"NTFY": {"topic": test_topic, "priority": 3}}

    # Create Notify instance from settings
    notify = Notify.from_settings(settings)

    # Mock the httpx.Client
    with patch("httpx.Client", mock_client):
        notify.publish("Test message", "Test title")

    # Verify the request was made correctly
    mock_client.return_value.__enter__.return_value.post.assert_called_once()

    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]

    # Verify URL and payload
    assert url == f"https://ntfy.sh/{test_topic}"
    payload = kwargs["json"]
    assert payload["message"] == "Test message"
    assert payload["title"] == "Test title"
    assert payload["priority"] == 3


@pytest.mark.asyncio
async def test_integration_with_notify_from_settings_async():
    """测试与 Notify.from_settings() 的异步集成"""
    from use_notify.notification import Notify

    # Create a mock for httpx.AsyncClient
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

    # Create settings
    settings = {"NTFY": {"topic": test_topic, "priority": 3}}

    # Create Notify instance from settings
    notify = Notify.from_settings(settings)

    # Mock the httpx.AsyncClient
    with patch("httpx.AsyncClient", mock_client):
        await notify.publish_async("Test message", "Test title")

    # Verify the request was made correctly
    mock_client.return_value.__aenter__.return_value.post.assert_called_once()

    # Get the call arguments
    call_args = mock_client.return_value.__aenter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]

    # Verify URL and payload
    assert url == f"https://ntfy.sh/{test_topic}"
    payload = kwargs["json"]
    assert payload["message"] == "Test message"
    assert payload["title"] == "Test title"
    assert payload["priority"] == 3


def test_integration_case_insensitive_channel_name():
    """测试不区分大小写的渠道名称"""
    from use_notify.notification import Notify

    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response

    # Test different case variations
    for channel_name in ["ntfy", "NTFY", "Ntfy", "nTfY"]:
        settings = {channel_name: {"topic": test_topic}}

        # Create Notify instance from settings
        notify = Notify.from_settings(settings)

        # Verify the channel was created
        assert len(notify.channels) == 1
        assert isinstance(notify.channels[0], Ntfy)
        assert notify.channels[0].config.topic == test_topic


if __name__ == "__main__":
    pytest.main()
