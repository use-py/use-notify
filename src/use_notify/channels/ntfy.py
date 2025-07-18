# -*- coding: utf-8 -*-
import logging
from typing import Dict, Any, Optional

import httpx

from .base import BaseChannel

logger = logging.getLogger(__name__)


class Ntfy(BaseChannel):
    """Ntfy.sh 通知渠道"""

    def __init__(self, config: dict):
        """
        初始化 Ntfy 渠道
        
        Args:
            config: 配置字典，必须包含 'topic'，可选包含 'base_url' 等参数
        """
        super().__init__(config)
        
        # 验证必需的配置参数
        if not hasattr(self.config, 'topic') or not self.config.topic:
            raise ValueError("Ntfy channel requires 'topic' in config")

    @property
    def api_url(self):
        """构建 ntfy.sh API URL"""
        # 检查是否有自定义 base_url，否则使用默认值
        if hasattr(self.config, 'base_url') and self.config.base_url:
            base_url = self.config.base_url.rstrip("/")
        else:
            base_url = "https://ntfy.sh"
        
        return f"{base_url}/{self.config.topic}"

    @property
    def headers(self):
        """构建请求头"""
        return {"Content-Type": "application/json; charset=utf-8"}

    def _prepare_payload(self, content: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        准备请求负载
        
        Args:
            content: 消息内容
            title: 消息标题（可选）
            
        Returns:
            dict: 请求负载
        """
        payload = {
            "message": content,
        }
        
        if title:
            payload["title"] = title
        
        # 添加高级功能支持
        # 优先级支持 (1-5)
        if hasattr(self.config, 'priority') and self.config.priority is not None:
            payload["priority"] = self.config.priority
        
        # 标签支持
        if hasattr(self.config, 'tags') and self.config.tags:
            payload["tags"] = self.config.tags
        
        # 点击 URL 支持
        if hasattr(self.config, 'click') and self.config.click:
            payload["click"] = self.config.click
        
        # 附件 URL 支持
        if hasattr(self.config, 'attach') and self.config.attach:
            payload["attach"] = self.config.attach
        
        # 操作支持
        if hasattr(self.config, 'actions') and self.config.actions:
            payload["actions"] = self.config.actions
            
        return payload

    def send(self, content: str, title: Optional[str] = None) -> None:
        """
        发送通知到 ntfy.sh
        
        Args:
            content: 消息内容
            title: 消息标题（可选）
        """
        payload = self._prepare_payload(content, title)
        
        with httpx.Client() as client:
            response = client.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
        
        logger.debug("`ntfy` send successfully")

    async def send_async(self, content: str, title: Optional[str] = None) -> None:
        """
        异步发送通知到 ntfy.sh
        
        Args:
            content: 消息内容
            title: 消息标题（可选）
        """
        payload = self._prepare_payload(content, title)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
        
        logger.debug("`ntfy` send successfully")