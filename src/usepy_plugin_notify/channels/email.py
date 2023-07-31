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
        self.smtp = smtplib.SMTP_SSL(self.config.server, self.config.port)
        self.smtp.connect(self.config.server, self.config.port)
        self.smtp.login(self.config.username, self.config.password)

    @staticmethod
    def build_message(content, title=None):
        message = MIMEText(content, 'html', 'utf-8')
        message['From'] = Header('notify', 'utf-8')
        subject = title or '消息提醒'
        message['Subject'] = Header(subject, 'utf-8')
        return message.as_string()

    def send(self, content, title=None):
        if not self.config.receivers:
            logger.error('请先设置接收邮箱<receivers>')
            return
        message = self.build_message(content, title)

        self.smtp.sendmail(self.config.sender, self.config.receivers, message)
        logger.debug('邮件通知推送成功')

    async def send_async(self, content, title=None):
        if not self.config.receivers:
            logger.error('请先设置接收邮箱<receivers>')
            return
        message = self.build_message(content, title)

        loop = asyncio.get_event_loop()
        sendmail_func = partial(self.smtp.sendmail, self.config.sender, self.config.receivers, message)
        await loop.run_in_executor(None, sendmail_func)
        logger.debug('邮件通知推送成功')

