# -*- coding: utf-8 -*-
import pytest
import httpx
import json
from unittest.mock import patch, MagicMock

from use_notify.channels.pushdeer import PushDeer


class TestPushDeer:
    """PushDeer通知渠道测试"""

    @pytest.fixture
    def pushdeer_config(self):
        """基本配置"""
        return {
            "token": "test_token"
        }

    @pytest.fixture
    def pushdeer_instance(self, pushdeer_config):
        """PushDeer实例"""
        return PushDeer(pushdeer_config)

    def test_api_url(self, pushdeer_instance):
        """测试API URL构建"""
        assert pushdeer_instance.api_url == "https://api2.pushdeer.com/message/push"

    def test_api_url_custom_base(self):
        """测试自定义base_url"""
        pushdeer = PushDeer({
            "token": "test_token",
            "base_url": "https://custom.pushdeer.com/"
        })
        assert pushdeer.api_url == "https://custom.pushdeer.com/message/push"

    def test_api_url_no_token(self):
        """测试没有token的情况"""
        pushdeer = PushDeer({})
        with pytest.raises(ValueError, match="PushDeer token .* required"):
            _ = pushdeer.api_url

    def test_prepare_params_text(self, pushdeer_instance):
        """测试文本消息参数准备"""
        params = pushdeer_instance._prepare_params("Hello World")
        assert params["pushkey"] == "test_token"
        assert params["text"] == "Hello World"
        assert params["type"] == "markdown"

    def test_prepare_params_markdown(self):
        """测试Markdown消息参数准备"""
        pushdeer = PushDeer({
            "token": "test_token",
            "type": "markdown"
        })
        params = pushdeer._prepare_params("# Hello\n\nWorld", "Test Title")
        assert params["pushkey"] == "test_token"
        assert params["text"] == "Test Title"
        assert params["desp"] == "# Hello\n\nWorld"
        assert params["type"] == "markdown"

    def test_prepare_params_image(self):
        """测试图片消息参数准备"""
        pushdeer = PushDeer({
            "token": "test_token",
            "type": "image"
        })
        params = pushdeer._prepare_params("https://example.com/image.jpg")
        assert params["pushkey"] == "test_token"
        assert params["desp"] == "https://example.com/image.jpg"
        assert params["type"] == "image"

    def test_prepare_params_invalid_type(self):
        """测试无效消息类型"""
        pushdeer = PushDeer({
            "token": "test_token",
            "type": "invalid"
        })
        params = pushdeer._prepare_params("Hello World")
        assert params["type"] == "markdown"  # 应该回退到text类型

    @patch("httpx.Client")
    def test_send_success(self, mock_client, pushdeer_instance):
        """测试发送成功"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"code": 0, "message": "success"}
        
        # 模拟客户端
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # 执行发送
        pushdeer_instance.send("Hello World", "Test Title")
        
        # 验证调用
        mock_client_instance.get.assert_called_once()
        args, kwargs = mock_client_instance.get.call_args
        assert args[0] == pushdeer_instance.api_url
        assert "params" in kwargs
        # 对于text类型，content会覆盖title作为text参数
        assert kwargs["params"]["text"] == "Hello World"

    @patch("httpx.Client")
    def test_send_api_error(self, mock_client, pushdeer_instance):
        """测试API返回错误"""
        # 模拟响应
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"code": 1, "error": "Invalid token"}
        
        # 模拟客户端
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # 执行发送，应该抛出异常
        with pytest.raises(RuntimeError, match="PushDeer API error: Invalid token"):
            pushdeer_instance.send("Hello World")

    @pytest.mark.asyncio
    async def test_send_async_success(self, pushdeer_instance):
        """测试异步发送成功"""
        # 创建一个真实的AsyncMock对象，它可以在await表达式中使用
        from unittest.mock import AsyncMock
        
        # 模拟响应
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        # 设置json方法为AsyncMock，返回值为字典
        mock_json = AsyncMock()
        mock_json.return_value = {"code": 0, "message": "success"}
        mock_response.json = mock_json
        
        # 模拟客户端
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        # 替换httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            # 执行发送
            await pushdeer_instance.send_async("Hello World", "Test Title")
            
            # 验证调用
            mock_client.get.assert_called_once()
            args, kwargs = mock_client.get.call_args
            assert args[0] == pushdeer_instance.api_url
            assert "params" in kwargs
            # 对于text类型，content会覆盖title作为text参数
            assert kwargs["params"]["text"] == "Hello World"

    @pytest.mark.asyncio
    async def test_send_async_api_error(self, pushdeer_instance):
        """测试异步API返回错误"""
        # 创建一个真实的AsyncMock对象，它可以在await表达式中使用
        from unittest.mock import AsyncMock
        
        # 模拟响应
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        # 设置json方法为AsyncMock，返回值为字典
        mock_json = AsyncMock()
        mock_json.return_value = {"code": 1, "error": "Invalid token"}
        mock_response.json = mock_json
        
        # 模拟客户端
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        
        # 替换httpx.AsyncClient
        with patch("httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client
            
            # 执行发送，应该抛出异常
            with pytest.raises(RuntimeError, match="PushDeer API error: Invalid token"):
                await pushdeer_instance.send_async("Hello World")