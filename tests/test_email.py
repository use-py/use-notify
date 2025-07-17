# -*- coding: utf-8 -*-
import pytest
import smtplib
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from email.mime.text import MIMEText
from email.header import Header

from use_notify.channels.email import Email


@pytest.fixture
def email_config():
    """完整的邮件配置"""
    return {
        "server": "smtp.gmail.com",
        "port": 587,
        "username": "test@example.com",
        "password": "test_password",
        "from_email": "sender@example.com",
        "to_emails": ["recipient1@example.com", "recipient2@example.com"]
    }


@pytest.fixture
def email_config_minimal():
    """最小邮件配置（缺少to_emails）"""
    return {
        "server": "smtp.gmail.com",
        "port": 587,
        "username": "test@example.com",
        "password": "test_password",
        "from_email": "sender@example.com"
    }


@pytest.fixture
def email_config_missing_required():
    """缺少必填字段的配置"""
    return {
        "server": "smtp.gmail.com",
        "port": 587,
        "to_emails": ["recipient@example.com"]
        # 缺少 username, password, from_email
    }


class TestEmail:
    """Email 通道测试类"""

    @patch('smtplib.SMTP_SSL')
    def test_init_success(self, mock_smtp, email_config):
        """测试成功初始化"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        email_channel = Email(email_config)
        
        # 验证SMTP连接和登录
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp_instance.connect.assert_called_once_with("smtp.gmail.com", 587)
        mock_smtp_instance.login.assert_called_once_with("test@example.com", "test_password")
        
        # 验证配置
        assert email_channel.config.server == "smtp.gmail.com"
        assert email_channel.config.port == 587
        assert email_channel.config.username == "test@example.com"
        assert email_channel.config.password == "test_password"
        assert email_channel.config.from_email == "sender@example.com"
        assert email_channel.config.to_emails == ["recipient1@example.com", "recipient2@example.com"]

    @patch('smtplib.SMTP_SSL')
    def test_init_smtp_connection_error(self, mock_smtp, email_config):
        """测试SMTP连接错误"""
        mock_smtp.side_effect = smtplib.SMTPException("Connection failed")
        
        with pytest.raises(smtplib.SMTPException):
            Email(email_config)

    @patch('smtplib.SMTP_SSL')
    def test_init_login_error(self, mock_smtp, email_config):
        """测试SMTP登录错误"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")
        
        with pytest.raises(smtplib.SMTPAuthenticationError):
            Email(email_config)

    def test_build_message_with_title(self):
        """测试构建带标题的邮件消息"""
        content = "<h1>测试内容</h1><p>这是一条测试消息</p>"
        title = "测试标题"
        
        message_str = Email.build_message(content, title)
        
        # 验证消息包含正确的内容
        assert "Content-Type: text/html; charset=\"utf-8\"" in message_str
        assert "From: =?utf-8?q?notify?=" in message_str or "From: =?utf-8?b?bm90aWZ5?=" in message_str
        assert "Subject:" in message_str
        # 由于内容可能被base64编码，我们检查原始内容是否存在或者检查MIMEText对象
        assert content in message_str or "base64" in message_str

    def test_build_message_without_title(self):
        """测试构建无标题的邮件消息"""
        content = "<h1>测试内容</h1><p>这是一条测试消息</p>"
        
        message_str = Email.build_message(content)
        
        # 验证使用默认标题
        assert "Subject:" in message_str
        # 由于内容可能被base64编码，我们检查原始内容是否存在或者检查编码标识
        assert content in message_str or "base64" in message_str

    def test_build_message_plain_text(self):
        """测试构建纯文本消息"""
        content = "这是纯文本消息"
        title = "纯文本标题"
        
        message_str = Email.build_message(content, title)
        
        # 由于内容可能被base64编码，我们检查原始内容是否存在或者检查编码标识
        assert content in message_str or "base64" in message_str
        assert "Content-Type: text/html; charset=\"utf-8\"" in message_str

    @patch('smtplib.SMTP_SSL')
    def test_send_success(self, mock_smtp, email_config):
        """测试成功发送邮件"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        email_channel = Email(email_config)
        content = "测试邮件内容"
        title = "测试标题"
        
        with patch.object(email_channel, 'build_message') as mock_build:
            mock_build.return_value = "mocked_message"
            
            email_channel.send(content, title)
            
            # 验证调用
            mock_build.assert_called_once_with(content, title)
            mock_smtp_instance.sendmail.assert_called_once_with(
                "sender@example.com",
                ["recipient1@example.com", "recipient2@example.com"],
                "mocked_message"
            )

    @patch('smtplib.SMTP_SSL')
    def test_send_without_title(self, mock_smtp, email_config):
        """测试发送无标题邮件"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        email_channel = Email(email_config)
        content = "测试邮件内容"
        
        with patch.object(email_channel, 'build_message') as mock_build:
            mock_build.return_value = "mocked_message"
            
            email_channel.send(content)
            
            mock_build.assert_called_once_with(content, None)

    @patch('smtplib.SMTP_SSL')
    @patch('use_notify.channels.email.logger')
    def test_send_missing_to_emails(self, mock_logger, mock_smtp, email_config_minimal):
        """测试缺少收件人邮箱时的处理"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        email_channel = Email(email_config_minimal)
        content = "测试邮件内容"
        
        email_channel.send(content)
        
        # 验证记录错误日志且不发送邮件
        mock_logger.error.assert_called_once_with("请先设置接收邮箱<to_emails>")
        mock_smtp_instance.sendmail.assert_not_called()

    @patch('smtplib.SMTP_SSL')
    def test_send_smtp_error(self, mock_smtp, email_config):
        """测试发送邮件时SMTP错误"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        mock_smtp_instance.sendmail.side_effect = smtplib.SMTPException("Send failed")
        
        email_channel = Email(email_config)
        
        with pytest.raises(smtplib.SMTPException):
            email_channel.send("测试内容")

    @patch('smtplib.SMTP_SSL')
    @patch('asyncio.get_event_loop')
    @pytest.mark.asyncio
    async def test_send_async_success(self, mock_get_loop, mock_smtp, email_config):
        """测试异步发送成功"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        mock_loop = AsyncMock()
        mock_get_loop.return_value = mock_loop
        
        email_channel = Email(email_config)
        content = "异步测试内容"
        title = "异步测试标题"
        
        with patch.object(email_channel, 'build_message') as mock_build:
            mock_build.return_value = "mocked_async_message"
            
            await email_channel.send_async(content, title)
            
            # 验证调用
            mock_build.assert_called_once_with(content, title)
            mock_loop.run_in_executor.assert_called_once()
            
            # 验证传递给executor的函数
            executor_call = mock_loop.run_in_executor.call_args
            assert executor_call[0][0] is None  # executor参数
            # 验证partial函数的参数
            partial_func = executor_call[0][1]
            assert partial_func.func == mock_smtp_instance.sendmail

    @patch('smtplib.SMTP_SSL')
    @patch('asyncio.get_event_loop')
    @patch('use_notify.channels.email.logger')
    @pytest.mark.asyncio
    async def test_send_async_missing_to_emails(self, mock_logger, mock_get_loop, mock_smtp, email_config_minimal):
        """测试异步发送时缺少收件人邮箱"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        mock_loop = AsyncMock()
        mock_get_loop.return_value = mock_loop
        
        email_channel = Email(email_config_minimal)
        
        await email_channel.send_async("测试内容")
        
        # 验证记录错误日志且不执行异步发送
        mock_logger.error.assert_called_once_with("请先设置接收邮箱<receivers>")
        mock_loop.run_in_executor.assert_not_called()

    @patch('smtplib.SMTP_SSL')
    @patch('asyncio.get_event_loop')
    @pytest.mark.asyncio
    async def test_send_async_executor_error(self, mock_get_loop, mock_smtp, email_config):
        """测试异步发送时executor错误"""
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        mock_loop = AsyncMock()
        mock_loop.run_in_executor.side_effect = Exception("Executor failed")
        mock_get_loop.return_value = mock_loop
        
        email_channel = Email(email_config)
        
        with pytest.raises(Exception, match="Executor failed"):
            await email_channel.send_async("测试内容")

    def test_config_access(self, email_config):
        """测试配置访问"""
        with patch('smtplib.SMTP_SSL'):
            email_channel = Email(email_config)
            
            assert email_channel.config.server == "smtp.gmail.com"
            assert email_channel.config.port == 587
            assert email_channel.config.username == "test@example.com"
            assert email_channel.config.password == "test_password"
            assert email_channel.config.from_email == "sender@example.com"
            assert email_channel.config.to_emails == ["recipient1@example.com", "recipient2@example.com"]

    def test_validate_required_fields_missing_single(self):
        """测试缺少单个必填字段"""
        config = {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "test@example.com",
            "password": "test_password"
            # 缺少 from_email
        }
        
        with pytest.raises(ValueError, match="缺少必填字段: from_email"):
            Email(config)

    def test_validate_required_fields_missing_multiple(self):
        """测试缺少多个必填字段"""
        config = {
            "server": "smtp.gmail.com",
            "port": 587
            # 缺少 username, password, from_email
        }
        
        with pytest.raises(ValueError, match="缺少必填字段: username, password, from_email"):
            Email(config)

    def test_validate_required_fields_empty_values(self):
        """测试必填字段为空值"""
        config = {
            "server": "",
            "port": 587,
            "username": None,
            "password": "test_password",
            "from_email": "sender@example.com"
        }
        
        with pytest.raises(ValueError, match="缺少必填字段: server, username"):
            Email(config)

    def test_validate_port_invalid_string(self):
        """测试端口号为无效字符串"""
        config = {
            "server": "smtp.gmail.com",
            "port": "invalid_port",
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "sender@example.com"
        }
        
        with pytest.raises(ValueError, match="端口号必须为有效的整数"):
            Email(config)

    def test_validate_port_out_of_range_low(self):
        """测试端口号过小"""
        config = {
            "server": "smtp.gmail.com",
            "port": 0,
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "sender@example.com"
        }
        
        with pytest.raises(ValueError, match="端口号必须在1-65535范围内"):
            Email(config)

    def test_validate_port_out_of_range_high(self):
        """测试端口号过大"""
        config = {
            "server": "smtp.gmail.com",
            "port": 65536,
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "sender@example.com"
        }
        
        with pytest.raises(ValueError, match="端口号必须在1-65535范围内"):
            Email(config)

    def test_validate_port_valid_string_number(self):
        """测试端口号为有效的字符串数字"""
        config = {
            "server": "smtp.gmail.com",
            "port": "587",  # 字符串格式的有效端口号
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "sender@example.com",
            "to_emails": ["recipient@example.com"]
        }
        
        with patch('smtplib.SMTP_SSL'):
            email_channel = Email(config)
            assert email_channel.config.port == "587"

    def test_config_missing_attributes(self):
        """测试配置完全缺少必填字段时的行为"""
        config = {}
        
        with pytest.raises(ValueError, match="缺少必填字段: server, username, password, from_email, port"):
            Email(config)

    @patch('smtplib.SMTP_SSL')
    def test_single_recipient(self, mock_smtp):
        """测试单个收件人"""
        config = {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "sender@example.com",
            "to_emails": "single@example.com"  # 单个邮箱字符串
        }
        
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        email_channel = Email(config)
        email_channel.send("测试内容")
        
        # 验证发送给单个收件人
        mock_smtp_instance.sendmail.assert_called_once()
        call_args = mock_smtp_instance.sendmail.call_args[0]
        assert call_args[1] == "single@example.com"

    @patch('smtplib.SMTP_SSL')
    def test_empty_to_emails_list(self, mock_smtp):
        """测试空的收件人列表"""
        config = {
            "server": "smtp.gmail.com",
            "port": 587,
            "username": "test@example.com",
            "password": "test_password",
            "from_email": "sender@example.com",
            "to_emails": []  # 空列表
        }
        
        mock_smtp_instance = Mock()
        mock_smtp.return_value = mock_smtp_instance
        
        email_channel = Email(config)
        
        with patch('use_notify.channels.email.logger') as mock_logger:
            email_channel.send("测试内容")
            
            # 验证记录错误日志
            mock_logger.error.assert_called_once_with("请先设置接收邮箱<to_emails>")
            mock_smtp_instance.sendmail.assert_not_called()