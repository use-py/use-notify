# -*- coding: utf-8 -*-
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

from use_notify.channels.wechat import WeChat


@pytest.fixture
def wechat_config():
    """基础配置"""
    return {
        "token": "test_token_123"
    }


@pytest.fixture
def wechat_config_with_mentions():
    """包含提及用户的配置"""
    return {
        "token": "test_token_123",
        "mentioned_list": ["@user1", "@user2"],
        "mentioned_mobile_list": ["13800138000", "13900139000"]
    }


@pytest.fixture
def wechat_channel(wechat_config):
    """基础 WeChat 通道实例"""
    return WeChat(wechat_config)


@pytest.fixture
def wechat_channel_with_mentions(wechat_config_with_mentions):
    """包含提及用户的 WeChat 通道实例"""
    return WeChat(wechat_config_with_mentions)


class TestWeChat:
    """WeChat 通道测试类"""

    def test_api_url_property(self, wechat_channel):
        """测试 API URL 生成"""
        expected_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test_token_123"
        assert wechat_channel.api_url == expected_url

    def test_headers_property(self, wechat_channel):
        """测试请求头"""
        expected_headers = {"Content-Type": "application/json"}
        assert wechat_channel.headers == expected_headers

    def test_build_api_body_basic(self, wechat_channel):
        """测试基础消息体构建"""
        title = "Test Title"
        content = "Test content"
        
        result = wechat_channel.build_api_body(title, content)
        
        expected = {
            "markdown": {
                "content": "## Test Title\n\nTest content"
            },
            "msgtype": "markdown"
        }
        
        assert result == expected

    def test_build_api_body_with_mentions(self, wechat_channel_with_mentions):
        """测试包含提及用户的消息体构建"""
        title = "Test Title"
        content = "Test content"
        
        result = wechat_channel_with_mentions.build_api_body(title, content)
        
        expected = {
            "markdown": {
                "content": "## Test Title\n\nTest content",
                "mentioned_list": ["@user1", "@user2"],
                "mentioned_mobile_list": ["13800138000", "13900139000"]
            },
            "msgtype": "markdown"
        }
        
        assert result == expected

    def test_build_api_body_no_title(self, wechat_channel):
        """测试无标题的消息体构建"""
        content = "Test content"
        
        result = wechat_channel.build_api_body(None, content)
        
        expected = {
            "markdown": {
                "content": "## None\n\nTest content"
            },
            "msgtype": "markdown"
        }
        
        assert result == expected

    @patch('httpx.Client')
    def test_send_success(self, mock_client, wechat_channel):
        """测试同步发送成功"""
        # 设置 mock
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # 调用发送方法
        wechat_channel.send("Test content", "Test Title")
        
        # 验证调用
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        
        assert call_args[1]['json']['msgtype'] == 'markdown'
        assert call_args[1]['json']['markdown']['content'] == '## Test Title\n\nTest content'
        assert call_args[1]['headers'] == {"Content-Type": "application/json"}

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_send_async_success(self, mock_client, wechat_channel):
        """测试异步发送成功"""
        # 设置 mock
        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # 调用异步发送方法
        await wechat_channel.send_async("Test content", "Test Title")
        
        # 验证调用
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        
        assert call_args[1]['json']['msgtype'] == 'markdown'
        assert call_args[1]['json']['markdown']['content'] == '## Test Title\n\nTest content'
        assert call_args[1]['headers'] == {"Content-Type": "application/json"}

    @patch('httpx.Client')
    def test_send_with_mentions(self, mock_client, wechat_channel_with_mentions):
        """测试发送包含提及用户的消息"""
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        wechat_channel_with_mentions.send("Test content", "Test Title")
        
        call_args = mock_client_instance.post.call_args
        json_data = call_args[1]['json']
        
        assert 'mentioned_list' in json_data['markdown']
        assert 'mentioned_mobile_list' in json_data['markdown']
        assert json_data['markdown']['mentioned_list'] == ["@user1", "@user2"]
        assert json_data['markdown']['mentioned_mobile_list'] == ["13800138000", "13900139000"]

    @patch('httpx.Client')
    def test_send_http_error(self, mock_client, wechat_channel):
        """测试发送时 HTTP 错误处理"""
        mock_client_instance = MagicMock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client_instance.post.side_effect = httpx.HTTPError("Network error")
        
        # 应该抛出异常
        with pytest.raises(httpx.HTTPError):
            wechat_channel.send("Test content", "Test Title")

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_send_async_http_error(self, mock_client, wechat_channel):
        """测试异步发送时 HTTP 错误处理"""
        mock_client_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        mock_client_instance.post.side_effect = httpx.HTTPError("Network error")
        
        # 应该抛出异常
        with pytest.raises(httpx.HTTPError):
            await wechat_channel.send_async("Test content", "Test Title")

    def test_config_access(self, wechat_channel):
        """测试配置访问"""
        assert wechat_channel.config.token == "test_token_123"

    def test_empty_mentions_config(self):
        """测试空提及列表配置"""
        config = {
            "token": "test_token",
            "mentioned_list": [],
            "mentioned_mobile_list": []
        }
        channel = WeChat(config)
        result = channel.build_api_body("Title", "Content")
        
        # 空列表不应该添加到消息体中
        assert 'mentioned_list' not in result['markdown']
        assert 'mentioned_mobile_list' not in result['markdown']