from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from use_notify import useNotifyChannel

EMAIL_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 465,
    "username": "user@example.com",
    "password": "secret",
    "from_email": "sender@example.com",
    "to_emails": ["receiver@example.com"],
}


@patch("smtplib.SMTP_SSL")
@patch("smtplib.SMTP")
def test_email_initialization_is_lazy(mock_smtp, mock_smtp_ssl):
    channel = useNotifyChannel.Email(EMAIL_CONFIG)

    mock_smtp.assert_not_called()
    mock_smtp_ssl.assert_not_called()
    assert channel.config.from_email == "sender@example.com"


def test_email_validates_required_fields():
    with pytest.raises(ValueError, match="缺少必填字段"):
        useNotifyChannel.Email({"server": "smtp.gmail.com", "port": 587})

    with pytest.raises(ValueError, match="缺少必填字段: port"):
        useNotifyChannel.Email({k: v for k, v in EMAIL_CONFIG.items() if k != "port"})

    with pytest.raises(ValueError, match="端口号必须为有效的整数"):
        useNotifyChannel.Email({**EMAIL_CONFIG, "port": "bad-port"})

    for port in (0, 65536):
        with pytest.raises(ValueError, match="端口号必须在1-65535范围内"):
            useNotifyChannel.Email({**EMAIL_CONFIG, "port": port})

    for port in (True, False):
        with pytest.raises(ValueError, match="端口号必须为有效的整数"):
            useNotifyChannel.Email({**EMAIL_CONFIG, "port": port})


@patch("smtplib.SMTP_SSL")
def test_email_send_uses_ssl_sendmail_and_quits(mock_smtp_ssl):
    smtp = mock_smtp_ssl.return_value
    channel = useNotifyChannel.Email(EMAIL_CONFIG)

    channel.send("hello", "title")

    mock_smtp_ssl.assert_called_once_with("smtp.gmail.com", 465)
    smtp.login.assert_called_once_with("user@example.com", "secret")
    smtp.sendmail.assert_called_once()
    args = smtp.sendmail.call_args[0]
    assert args[0] == "sender@example.com"
    assert args[1] == ["receiver@example.com"]
    assert "title" in args[2]
    smtp.quit.assert_called_once_with()


@patch("smtplib.SMTP")
def test_email_send_uses_starttls_when_configured(mock_smtp):
    smtp = mock_smtp.return_value
    channel = useNotifyChannel.Email(
        {
            **EMAIL_CONFIG,
            "port": 587,
            "use_ssl": False,
            "use_tls": True,
        }
    )

    channel.send("hello", "title")

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    smtp.starttls.assert_called_once_with()
    smtp.login.assert_called_once_with("user@example.com", "secret")
    smtp.sendmail.assert_called_once()
    smtp.quit.assert_called_once_with()


@patch("smtplib.SMTP")
def test_email_send_uses_starttls_by_default_for_587(mock_smtp):
    smtp = mock_smtp.return_value
    channel = useNotifyChannel.Email({**EMAIL_CONFIG, "port": 587})

    channel.send("hello", "title")

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    smtp.starttls.assert_called_once_with()
    smtp.login.assert_called_once_with("user@example.com", "secret")
    smtp.sendmail.assert_called_once()


@patch("smtplib.SMTP")
def test_email_send_respects_disabled_starttls(mock_smtp):
    smtp = mock_smtp.return_value
    channel = useNotifyChannel.Email({**EMAIL_CONFIG, "port": 587, "use_tls": False})

    channel.send("hello", "title")

    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    smtp.starttls.assert_not_called()
    smtp.login.assert_called_once_with("user@example.com", "secret")


@patch("smtplib.SMTP_SSL")
@patch("asyncio.get_running_loop")
@pytest.mark.asyncio
async def test_email_send_async_uses_executor(mock_get_running_loop, mock_smtp_ssl):
    smtp = mock_smtp_ssl.return_value
    loop = MagicMock()
    loop.run_in_executor = AsyncMock(return_value=None)
    mock_get_running_loop.return_value = loop
    channel = useNotifyChannel.Email(EMAIL_CONFIG)

    await channel.send_async("hello", "title")

    loop.run_in_executor.assert_awaited_once()
    partial_send = loop.run_in_executor.call_args[0][1]
    partial_send()
    smtp.sendmail.assert_called_once()


@patch("smtplib.SMTP_SSL")
@patch("smtplib.SMTP")
@patch("use_notify.channels.email.logger")
def test_email_send_without_receivers_only_logs(mock_logger, mock_smtp, mock_smtp_ssl):
    channel = useNotifyChannel.Email({k: v for k, v in EMAIL_CONFIG.items() if k != "to_emails"})

    channel.send("hello")

    mock_logger.error.assert_called_once_with("请先设置接收邮箱<to_emails>")
    mock_smtp.assert_not_called()
    mock_smtp_ssl.assert_not_called()


@patch("smtplib.SMTP_SSL")
@patch("smtplib.SMTP")
@patch("use_notify.channels.email.logger")
@pytest.mark.asyncio
async def test_email_send_async_without_receivers_only_logs(mock_logger, mock_smtp, mock_smtp_ssl):
    channel = useNotifyChannel.Email({k: v for k, v in EMAIL_CONFIG.items() if k != "to_emails"})

    await channel.send_async("hello")

    mock_logger.error.assert_called_once_with("请先设置接收邮箱<to_emails>")
    mock_smtp.assert_not_called()
    mock_smtp_ssl.assert_not_called()


@patch("smtplib.SMTP_SSL")
def test_email_close_falls_back_when_quit_fails(mock_smtp_ssl):
    smtp = mock_smtp_ssl.return_value
    smtp.quit.side_effect = OSError("socket already closed")
    channel = useNotifyChannel.Email(EMAIL_CONFIG)

    channel.send("hello")

    smtp.quit.assert_called_once_with()
    smtp.close.assert_called_once_with()
