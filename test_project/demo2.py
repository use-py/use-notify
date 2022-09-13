# -*- coding: utf-8 -*-
from notify.notification import Notify

trigger = "notify.channels.bark.Bark"
channels = {
    'BARK': {
        'TOKEN': "123"
    }
}
notify = Notify(trigger, channels)
notify.send_message(content="爬虫报错啦！！！！", title="数据中心报错")
