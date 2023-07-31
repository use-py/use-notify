# -*- coding: utf-8 -*-
import asyncio
from usepy.plugin import useNotify, useNotifyChannel

notify = useNotify()
notify.add(
    # 添加多个通知渠道
    useNotifyChannel.Bark({"token": "xxx"}),

)

asyncio.run(
    notify.publish_async(title="消息标题", content="消息正文")
)
