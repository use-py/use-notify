# -*- coding: utf-8 -*-
from notify import useNotify, channels

notify = useNotify()
notify.add(
    # 添加多个通知渠道
    channels.Bark({"token": ""}),
    channels.Ding({
        "token": "",
        "at_all": True
    })
)

notify.publish(title="消息标题", content="消息正文")
