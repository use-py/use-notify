import pytest
from unittest.mock import patch, MagicMock

from use_notify.channels.bark import Bark


@pytest.fixture
def bark_config():
    return {
        "token": "your_key",
        "sound": "minuet",
        "icon": "https://day.app/assets/images/avatar.jpg",
        "group": "test",
        "badge": 1,
        "url": "https://mritd.com"
    }


def test_bark_send(bark_config):
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response
    
    # Create Bark instance
    bark = Bark(bark_config)
    
    # Mock the httpx.Client
    with patch('httpx.Client', mock_client):
        bark.send("Test Bark Server", "Test Title")
    
    # Verify the request was made correctly
    mock_client.return_value.__enter__.return_value.post.assert_called_once()
    
    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]
    
    # Verify URL and headers
    assert url == "https://api.day.app/your_key"
    assert kwargs["headers"]["Content-Type"] == "application/json; charset=utf-8"
    
    # Verify payload
    payload = kwargs["json"]
    assert payload["body"] == "Test Bark Server"
    assert payload["title"] == "Test Title"
    assert payload["badge"] == 1
    assert payload["sound"] == "minuet"
    assert payload["icon"] == "https://day.app/assets/images/avatar.jpg"
    assert payload["group"] == "test"
    assert payload["url"] == "https://mritd.com"
    
    # Verify response handling
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_bark_send_async(bark_config):
    # Create a mock for httpx.AsyncClient
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
    
    # Create Bark instance
    bark = Bark(bark_config)
    
    # Mock the httpx.AsyncClient
    with patch('httpx.AsyncClient', mock_client):
        await bark.send_async("Test Bark Server", "Test Title")
    
    # Verify the request was made correctly
    mock_client.return_value.__aenter__.return_value.post.assert_called_once()
    
    # Get the call arguments
    call_args = mock_client.return_value.__aenter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]
    
    # Verify URL and headers
    assert url == "https://api.day.app/your_key"
    assert kwargs["headers"]["Content-Type"] == "application/json; charset=utf-8"
    
    # Verify payload
    payload = kwargs["json"]
    assert payload["body"] == "Test Bark Server"
    assert payload["title"] == "Test Title"
    assert payload["badge"] == 1
    assert payload["sound"] == "minuet"
    assert payload["icon"] == "https://day.app/assets/images/avatar.jpg"
    assert payload["group"] == "test"
    assert payload["url"] == "https://mritd.com"
    
    # Verify response handling
    mock_response.raise_for_status.assert_called_once()


@pytest.fixture
def custom_bark_config():
    return {
        "token": "your_key",
        "base_url": "https://bark.example.com",
        "sound": "minuet",
        "icon": "https://day.app/assets/images/avatar.jpg",
        "group": "test",
        "badge": 1,
        "url": "https://mritd.com"
    }


def test_bark_custom_url(custom_bark_config):
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response
    
    # Create Bark instance with custom base URL
    bark = Bark(custom_bark_config)
    
    # Mock the httpx.Client
    with patch('httpx.Client', mock_client):
        bark.send("Test Bark Server", "Test Title")
    
    # Verify the request was made correctly
    mock_client.return_value.__enter__.return_value.post.assert_called_once()
    
    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    
    # Verify custom URL is used
    assert url == "https://bark.example.com/your_key"
    
    # Verify response handling
    mock_response.raise_for_status.assert_called_once()


def test_bark_url_with_trailing_slash():
    # Config with trailing slash in base_url
    config = {
        "token": "your_key",
        "base_url": "https://bark.example.com/"
    }
    
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response
    
    # Create Bark instance
    bark = Bark(config)
    
    # Mock the httpx.Client
    with patch('httpx.Client', mock_client):
        bark.send("Test Content")
    
    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    
    # Verify URL doesn't have double slashes
    assert url == "https://bark.example.com/your_key"