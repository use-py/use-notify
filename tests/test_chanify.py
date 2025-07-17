import pytest
from unittest.mock import patch, MagicMock

from use_notify.channels.chanify import Chanify


@pytest.fixture
def chanify_config():
    return {
        "token": "your_token"
    }


@pytest.fixture
def custom_chanify_config():
    return {
        "token": "your_token",
        "base_url": "https://chanify.example.com"
    }


def test_chanify_send(chanify_config):
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response
    
    # Create Chanify instance
    chanify = Chanify(chanify_config)
    
    # Mock the httpx.Client
    with patch('httpx.Client', mock_client):
        chanify.send("Test Content", "Test Title")
    
    # Verify the request was made correctly
    mock_client.return_value.__enter__.return_value.post.assert_called_once()
    
    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]
    
    # Verify URL and headers
    assert url == "https://api.chanify.net/v1/sender/your_token"
    assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
    
    # Verify payload
    payload = kwargs["data"]
    assert payload["text"] == "Test Title\nTest Content"


@pytest.mark.asyncio
async def test_chanify_send_async(chanify_config):
    # Create a mock for httpx.AsyncClient
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
    
    # Create Chanify instance
    chanify = Chanify(chanify_config)
    
    # Mock the httpx.AsyncClient
    with patch('httpx.AsyncClient', mock_client):
        await chanify.send_async("Test Content", "Test Title")
    
    # Verify the request was made correctly
    mock_client.return_value.__aenter__.return_value.post.assert_called_once()
    
    # Get the call arguments
    call_args = mock_client.return_value.__aenter__.return_value.post.call_args
    url = call_args[0][0]
    kwargs = call_args[1]
    
    # Verify URL and headers
    assert url == "https://api.chanify.net/v1/sender/your_token"
    assert kwargs["headers"]["Content-Type"] == "application/x-www-form-urlencoded"
    
    # Verify payload
    payload = kwargs["data"]
    assert payload["text"] == "Test Title\nTest Content"


def test_chanify_custom_url(custom_chanify_config):
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response
    
    # Create Chanify instance with custom base URL
    chanify = Chanify(custom_chanify_config)
    
    # Mock the httpx.Client
    with patch('httpx.Client', mock_client):
        chanify.send("Test Content", "Test Title")
    
    # Verify the request was made correctly
    mock_client.return_value.__enter__.return_value.post.assert_called_once()
    
    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    
    # Verify custom URL is used
    assert url == "https://chanify.example.com/v1/sender/your_token"


def test_chanify_url_with_trailing_slash():
    # Config with trailing slash in base_url
    config = {
        "token": "your_token",
        "base_url": "https://chanify.example.com/"
    }
    
    # Create a mock for httpx.Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_client.return_value.__enter__.return_value.post.return_value = mock_response
    
    # Create Chanify instance
    chanify = Chanify(config)
    
    # Mock the httpx.Client
    with patch('httpx.Client', mock_client):
        chanify.send("Test Content")
    
    # Get the call arguments
    call_args = mock_client.return_value.__enter__.return_value.post.call_args
    url = call_args[0][0]
    
    # Verify URL doesn't have double slashes
    assert url == "https://chanify.example.com/v1/sender/your_token"