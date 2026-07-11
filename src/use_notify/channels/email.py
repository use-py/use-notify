# -*- coding: utf-8 -*-
import asyncio
import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from functools import partial

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Email(BaseChannel):
    """邮件消息通知"""

    def __init__(self, config):
        super().__init__(config)
        self._validate_required_fields()

    def _validate_required_fields(self):
        """校验必填字段"""
        required_fields = ["server", "username", "password", "from_email"]
        missing_fields = []

        for field in required_fields:
            if not hasattr(self.config, field) or not getattr(self.config, field):
                missing_fields.append(field)

        # 单独校验端口号
        if not self.config.port and not isinstance(self.config.port, int):
            missing_fields.append("port")

        if missing_fields:
            raise ValueError(f"缺少必填字段: {', '.join(missing_fields)}")

        # 校验端口号是否为有效整数
        try:
            port = int(self.config.port)
            if port <= 0 or port > 65535:
                raise ValueError("端口号必须在1-65535范围内")
        except (ValueError, TypeError) as e:
            if "invalid literal" in str(e):
                raise ValueError("端口号必须为有效的整数")
            raise

    @staticmethod
    def build_message(content, title=None):
        message = MIMEText(content, "html", "utf-8")
        message["From"] = Header("notify", "utf-8")
        subject = title or "消息提醒"
        message["Subject"] = Header(subject, "utf-8")
        return message.as_string()

    def send(self, content, title=None):
        if not self.config.to_emails:
            logger.error("请先设置接收邮箱<to_emails>")
            return
        message = self.build_message(content, title)

        self._send_message(message)
        logger.debug("邮件通知推送成功")

    async def send_async(self, content, title=None):
        if not self.config.to_emails:
            logger.error("请先设置接收邮箱<receivers>")
            return
        message = self.build_message(content, title)

        loop = asyncio.get_running_loop()
        sendmail_func = partial(self._send_message, message)
        await loop.run_in_executor(None, sendmail_func)
        logger.debug("邮件通知推送成功")

    def _send_message(self, message):
        smtp = self._connect()
        try:
            smtp.sendmail(self.config.from_email, self.config.to_emails, message)
        finally:
            self._close(smtp)

    def _connect(self):
        port = int(self.config.port)
        if self._use_ssl(port):
            smtp = smtplib.SMTP_SSL(self.config.server, port)
        else:
            smtp = smtplib.SMTP(self.config.server, port)
            if self._use_tls(port):
                smtp.starttls()

        smtp.login(self.config.username, self.config.password)
        return smtp

    def _use_ssl(self, port: int) -> bool:
        if "use_ssl" in self.config:
            return bool(self.config.use_ssl)
        if "use_tls" in self.config and self.config.use_tls:
            return False
        return port == 465

    def _use_tls(self, port: int) -> bool:
        if "use_tls" in self.config:
            return bool(self.config.use_tls)
        return not self._use_ssl(port) and port == 587

    @staticmethod
    def _close(smtp):
        try:
            smtp.quit()
        except (OSError, smtplib.SMTPException):
            smtp.close()
