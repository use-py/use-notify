### 一个简单可扩展的消息通知库

#### 安装
> pip install ml-simple-notify

#### 使用
```python
from notify.notification import Notify
# import settings

notify = Notify.from_settings()
notify.send_message(content="content", title="title")
```

settings模板文件可参考default_settings.py

```python
# 消息通知渠道的配置项
CHANNELS = {
    'DING': {
        'ACCESS_TOKEN': "ee45bea8e9b5029a9c71*********6f0d98cff232a6b35e52df2",
        'AT_ALL': True
    }
}
# 消息通知启用项目
TRIGGERS = {
    # 开启库中钉钉消息通知，对应的CHANNELS中需要配置钉钉的token
    'notify.channels.ding.Ding': 100,
}
```

#### 自己开发消息通知
```python
from notify.notification import Notification


class Custom(Notification):
    """自定义消息"""
    def __init__(self, settings):
        self.settings = settings

    def send_message(self, content, title=None):
        print(f"来自自定义的消息{content}")

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)
```
随后在settings.py文件中的TRIGGERS开启此通知
```python
TRIGGERS = {
    'channels.custom.Custom': 100,
}
```
触发器的值为字典类型，键名为包路径，键值为优先级，值越小优先级越高