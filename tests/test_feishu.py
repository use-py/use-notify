# -*- coding: utf-8 -*-
import pytest
from unittest.mock import Mock, patch, AsyncMock

from use_notify.channels.feishu import Feishu


@pytest.fixture
def feishu_config():
    return {
        "token": "test_token_123",
        "at_all": True,
        "at_user_ids": ["ou_f9fa825035541c7e205e0377b3111111", "ou_f9fa825035541c7e205e0377b3222222"],
    }


@pytest.fixture
def feishu_config_minimal():
    return {"token": "test_token_123"}


@pytest.fixture
def feishu_channel(feishu_config):
    return Feishu(feishu_config)


@pytest.fixture
def feishu_channel_minimal(feishu_config_minimal):
    return Feishu(feishu_config_minimal)


class TestFeishu:
    def test_api_url(self, feishu_channel):
        expected_url = "https://open.feishu.cn/open-apis/bot/v2/hook/test_token_123"
        assert feishu_channel.api_url == expected_url

    def test_headers(self, feishu_channel):
        expected_headers = {"Content-Type": "application/json"}
        assert feishu_channel.headers == expected_headers

    def test_build_api_body_with_title(self, feishu_channel):
        content = "测试消息内容"
        title = "自定义标题"

        result = feishu_channel.build_api_body(content, title)
        expected = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {"tag": "text", "text": content},
                                {"tag": "at", "user_id": "all"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3111111"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3222222"}
                            ]
                        ]
                    }
                }
            }
        }
        assert result == expected

    def test_build_api_body_without_title(self, feishu_channel):
        content = "测试消息内容"

        result = feishu_channel.build_api_body(content)

        expected = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "消息提醒",
                        "content": [
                            [
                                {"tag": "text", "text": content},
                                {"tag": "at", "user_id": "all"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3111111"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3222222"}
                            ]
                        ]
                    }
                }
            }
        }
        assert result == expected

    def test_build_api_body_minimal_config(self, feishu_channel_minimal):
        content = "测试消息内容"
        title = "测试标题"

        result = feishu_channel_minimal.build_api_body(content, title)

        expected = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {"tag": "text", "text": content},
                            ]
                        ]
                    }
                }
            }
        }
        assert result == expected

    @patch('httpx.Client')
    def test_send(self, mock_client, feishu_channel):
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance

        content = "测试消息"
        title = "测试标题"

        feishu_channel.send(content, title)

        expected_body = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {"tag": "text", "text": content},
                                {"tag": "at", "user_id": "all"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3111111"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3222222"}
                            ]
                        ]
                    }
                }
            }
        }

        mock_client_instance.post.assert_called_once_with(
            feishu_channel.api_url,
            json=expected_body,
            headers=feishu_channel.headers
        )

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_send_async(self, mock_async_client, feishu_channel):
        mock_client_instance = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        content = "测试异步消息"
        title = "异步标题"

        await feishu_channel.send_async(content, title)

        expected_body = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {"tag": "text", "text": content},
                                {"tag": "at", "user_id": "all"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3111111"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3222222"}
                            ]
                        ]
                    }
                }
            }
        }

        mock_client_instance.post.assert_called_once_with(
            feishu_channel.api_url,
            json=expected_body,
            headers=feishu_channel.headers
        )

    @patch('httpx.Client')
    def test_send_without_title(self, mock_client, feishu_channel):
        mock_client_instance = Mock()
        mock_client.return_value.__enter__.return_value = mock_client_instance

        content = "测试消息"

        feishu_channel.send(content)

        expected_body = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "消息提醒",
                        "content": [
                            [
                                {"tag": "text", "text": content},
                                {"tag": "at", "user_id": "all"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3111111"},
                                {"tag": "at", "user_id": "ou_f9fa825035541c7e205e0377b3222222"}
                            ]
                        ]
                    }
                }
            }
        }

        mock_client_instance.post.assert_called_once_with(
            feishu_channel.api_url,
            json=expected_body,
            headers=feishu_channel.headers
        )

    def test_config_access(self, feishu_channel):
        assert feishu_channel.config.token == "test_token_123"
        assert feishu_channel.config.at_all is True
        assert feishu_channel.config.at_user_ids == ["ou_f9fa825035541c7e205e0377b3111111",
                                                     "ou_f9fa825035541c7e205e0377b3222222"]

    def test_config_missing_attributes(self, feishu_channel_minimal):
        # 测试配置中缺少可选属性时的行为
        assert feishu_channel_minimal.config.token == "test_token_123"
        assert not hasattr(feishu_channel_minimal.config, 'at_all') or not feishu_channel_minimal.config.at_all
        assert not hasattr(feishu_channel_minimal.config,
                           'at_user_ids') or not feishu_channel_minimal.config.at_user_ids
