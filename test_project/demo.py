# -*- coding: utf-8 -*-
from notify.notification import Notify
import settings


notify = Notify.from_settings(settings=settings)
notify.send_message(content="爬虫报错啦！！！！", title="数据中心报错")