"""

notify = useNotify.wechat(
    configs={...}
)

notify.send("")

useNotify(
    channels={},
    triggers={}
)

"""

from src.notify.notification import Notify

useNotify = Notify
