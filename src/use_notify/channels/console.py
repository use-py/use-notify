from .base import BaseChannel


class Console(BaseChannel):
    """控制台通知渠道（用于演示）"""

    def __init__(self, config=None):
        super().__init__(config or {})

    def send(self, content, title=None):
        """发送通知到控制台"""
        title_display = title or "消息提醒"
        print(f"\n📢 [默认实例通知] {title_display}")
        print(f"📝 {content}")
        print("-" * 50)

    async def send_async(self, content, title=None):
        """异步发送通知到控制台"""
        title_display = title or "消息提醒"
        print(f"\n📢 [默认实例异步通知] {title_display}")
        print(f"📝 {content}")
        print("-" * 50)
