# 配置管理 API

配置管理 API 提供了对 Nacos 配置的基本操作，包括获取、发布、删除配置以及监听配置变更。

## 获取配置

```python
async def get_config(
    self,
    data_id: str,
    group: str = "DEFAULT_GROUP"
) -> str:
    """
    获取配置内容

    参数:
        data_id: 配置 ID
        group: 配置分组，默认为 DEFAULT_GROUP
    
    返回:
        配置内容字符串
    
    异常:
        NacosRequestException: 获取配置失败
    """
```

## 发布配置

```python
async def publish_config(
    self,
    data_id: str,
    group: str,
    content: str
) -> bool:
    """
    发布配置

    参数:
        data_id: 配置 ID
        group: 配置分组
        content: 配置内容
    
    返回:
        是否发布成功
    """
```

## 删除配置

```python
async def remove_config(
    self,
    data_id: str,
    group: str = "DEFAULT_GROUP"
) -> bool:
    """
    删除配置

    参数:
        data_id: 配置 ID
        group: 配置分组，默认为 DEFAULT_GROUP
    
    返回:
        是否删除成功
    """
```

## 监听配置

```python
async def add_config_watcher(
    self,
    data_id: str,
    group: str,
    callback: Callable[[str, str, str, str], Awaitable[None]]
) -> None:
    """
    添加配置监听器

    参数:
        data_id: 配置 ID
        group: 配置分组
        callback: 配置变更回调函数
            callback 参数: (namespace, data_id, group, content)
    """
```

## 使用示例

```python
from use_nacos import NacosClient

client = NacosClient("http://localhost:8848")

# 获取配置
config = await client.get_config("app.yaml", "DEFAULT_GROUP")
print(f"配置内容: {config}")

# 发布配置
success = await client.publish_config(
    "app.yaml",
    "DEFAULT_GROUP",
    "name: myapp\nversion: 1.0.0"
)
print(f"发布配置: {'成功' if success else '失败'}")

# 监听配置变更
async def on_config_change(namespace, data_id, group, content):
    print(f"配置已更新: {content}")

await client.add_config_watcher(
    "app.yaml",
    "DEFAULT_GROUP",
    on_config_change
)
```