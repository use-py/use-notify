# -*- coding: utf-8 -*-
import pytest
from unittest.mock import Mock, patch, AsyncMock

from use_notify.channels.ding import Ding


@pytest.fixture
def ding_config():
    return {
        "token": "test_token_123",
        "at_all": True,
        "at_mobiles": ["13800138000", "13900139000"],
        "at_user_ids": ["user1", "user2"]
    }


@pytest.fixture
def ding_config_minimal():
    return {"token": "test_token_123"}


@pytest.fixture
def ding_channel(ding_config):
    return Ding(ding_config)


@pytest.fixture
def ding_channel_minimal(ding_config_minimal):
    return Ding(ding_config_minimal)


class TestDing:
    def test_api_url(self, ding_channel):
        expected_url = "https://oapi.dingtalk.com/robot/send?access_token=test_token_123"
        assert ding_channel.api_url == expected_url

    def test_headers(self, ding_channel):
        expected_headers = {"Content-Type": "application/json"}
        assert ding_channel.headers == expected_headers

    def test_build_api_body_with_title(self, ding_channel):
        content = "测试消息内容"
        title = "自定义标题"
        
        result = ding_channel.build_api_body(content, title)
        
        expected = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": content},
            "at": {
                "isAtAll": True,
                "atMobiles": ["13800138000", "13900139000"],
                "atUserIds": ["user1", "user2"]
            },
        }
        assert result == expected

    def test_build_api_body_without_title(self, ding_channel):
        content = "测试消息内容"
        
        result = ding_channel.build_api_body(content)
        
        expected = {
            "msgtype": "markdown",
            "markdown": {"title": "消息提醒", "text": content},
            "at": {
                "isAtAll": True,
                "atMobiles": ["13800138000", "13900139000"],
                "atUserIds": ["user1", "user2"]
            },
        }
        assert result == expected

    def test_build_api_body_minimal_config(self, ding_channel_minimal):
        content = "测试消息内容"
        title = "测试标题"
        
        result = ding_channel_minimal.build_api_body(content, title)
        
        expected = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": content},
            "at": {},
        }
        assert result == expected

    @patch('httpx.Client')
    def test_send(self, mock_client, ding_channel):
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        content = "测试消息"
        title = "测试标题"
        
        ding_channel.send(content, title)
        
        expected_body = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": content},
            "at": {
                "isAtAll": True,
                "atMobiles": ["13800138000", "13900139000"],
                "atUserIds": ["user1", "user2"]
            },
        }
        
        mock_client_instance.post.assert_called_once_with(
            ding_channel.api_url,
            json=expected_body,
            headers=ding_channel.headers
        )

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_send_async(self, mock_async_client, ding_channel):
        mock_client_instance = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance
        
        content = "测试异步消息"
        title = "异步标题"
        
        await ding_channel.send_async(content, title)
        
        expected_body = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": content},
            "at": {
                "isAtAll": True,
                "atMobiles": ["13800138000", "13900139000"],
                "atUserIds": ["user1", "user2"]
            },
        }
        
        mock_client_instance.post.assert_called_once_with(
            ding_channel.api_url,
            json=expected_body,
            headers=ding_channel.headers
        )

    @patch('httpx.Client')
    def test_send_without_title(self, mock_client, ding_channel):
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        content = "测试消息"
        
        ding_channel.send(content)
        
        expected_body = {
            "msgtype": "markdown",
            "markdown": {"title": "消息提醒", "text": content},
            "at": {
                "isAtAll": True,
                "atMobiles": ["13800138000", "13900139000"],
                "atUserIds": ["user1", "user2"]
            },
        }
        
        mock_client_instance.post.assert_called_once_with(
            ding_channel.api_url,
            json=expected_body,
            headers=ding_channel.headers
        )

    def test_config_access(self, ding_channel):
        assert ding_channel.config.token == "test_token_123"
        assert ding_channel.config.at_all is True
        assert ding_channel.config.at_mobiles == ["13800138000", "13900139000"]
        assert ding_channel.config.at_user_ids == ["user1", "user2"]

    def test_config_missing_attributes(self, ding_channel_minimal):
        # 测试配置中缺少可选属性时的行为
        assert ding_channel_minimal.config.token == "test_token_123"
        assert not hasattr(ding_channel_minimal.config, 'at_all') or not ding_channel_minimal.config.at_all
        assert not hasattr(ding_channel_minimal.config, 'at_mobiles') or not ding_channel_minimal.config.at_mobiles
        assert not hasattr(ding_channel_minimal.config, 'at_user_ids') or not ding_channel_minimal.config.at_user_ids