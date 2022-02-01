# -*- coding: utf-8 -*-
import logging
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from notify.notification import Notification

logger = logging.getLogger(__name__)


class Email(Notification):
    """邮件消息通知"""
    def __init__(self, settings):
        self.server = settings.EMAIL.SERVER
        self.port = settings.EMAIL.PORT
        self.sender = settings.EMAIL.SENDER
        self.username = settings.EMAIL.USERNAME
        self.password = settings.EMAIL.PASSWORD
        self.receivers = settings.EMAIL.RECEIVERS

        self.smtp = smtplib.SMTP_SSL(self.server, self.port)
        self.smtp.connect(self.server, self.port)
        self.smtp.login(self.username, self.password)

    def send_message(self, content, title=None):
        if not self.receivers:
            logger.error('请先设置接收邮箱<receivers>')
            return
        message = MIMEText(content, 'html', 'utf-8')
        message['From'] = Header('notify', 'utf-8')
        subject = title or '消息提醒'
        message['Subject'] = Header(subject, 'utf-8')

        self.smtp.sendmail(self.sender, self.receivers, message.as_string())
        logger.debug('邮件通知推送成功')

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)
