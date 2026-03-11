import asyncio
import smtplib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from use_notify import useNotifyChannel


EMAIL_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": "user@example.com",
    "password": "secret",
    "from_email": "sender@example.com",
    "to_emails": ["receiver@example.com"],
}


@patch("smtplib.SMTP_SSL")
def test_email_initializes_and_logs_in(mock_smtp):
    smtp = mock_smtp.return_value

    channel = useNotifyChannel.Email(EMAIL_CONFIG)

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    smtp.connect.assert_called_once_with("smtp.gmail.com", 587)
    smtp.login.assert_called_once_with("user@example.com", "secret")
    assert channel.config.from_email == "sender@example.com"


def test_email_validates_required_fields():
    with pytest.raises(ValueError, match="缺少必填字段"):
        useNotifyChannel.Email({"server": "smtp.gmail.com", "port": 587})

    with pytest.raises(ValueError, match="端口号必须为有效的整数"):
        useNotifyChannel.Email({**EMAIL_CONFIG, "port": "bad-port"})


@patch("smtplib.SMTP_SSL")
def test_email_send_uses_sendmail(mock_smtp):
    smtp = mock_smtp.return_value
    channel = useNotifyChannel.Email(EMAIL_CONFIG)

    channel.send("hello", "title")

    smtp.sendmail.assert_called_once()
    args = smtp.sendmail.call_args[0]
    assert args[0] == "sender@example.com"
    assert args[1] == ["receiver@example.com"]
    assert "title" in args[2]


@patch("smtplib.SMTP_SSL")
@patch("asyncio.get_event_loop")
@pytest.mark.asyncio
async def test_email_send_async_uses_executor(mock_get_event_loop, mock_smtp):
    smtp = mock_smtp.return_value
    loop = MagicMock()
    loop.run_in_executor = AsyncMock(return_value=None)
    mock_get_event_loop.return_value = loop
    channel = useNotifyChannel.Email(EMAIL_CONFIG)

    await channel.send_async("hello", "title")

    loop.run_in_executor.assert_awaited_once()
    partial_send = loop.run_in_executor.call_args[0][1]
    partial_send()
    smtp.sendmail.assert_called_once()


@patch("smtplib.SMTP_SSL")
@patch("use_notify.channels.email.logger")
def test_email_send_without_receivers_only_logs(mock_logger, mock_smtp):
    channel = useNotifyChannel.Email({k: v for k, v in EMAIL_CONFIG.items() if k != "to_emails"})

    channel.send("hello")

    mock_logger.error.assert_called_once_with("请先设置接收邮箱<to_emails>")
