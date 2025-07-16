# 服务发现 API

服务发现 API 提供了服务注册、注销、查询等功能。

## 注册服务实例

```python
async def register_instance(
    self,
    service_name: str,
    ip: str,
    port: int,
    metadata: dict | None = None
) -> bool:
    """
    注册服务实例

    参数:
        service_name: 服务名称
        ip: 实例 IP
        port: 实例端口
        metadata: 实例元数据（可选）
    
    返回:
        是否注册成功
    """
```

## 注销服务实例

```python
async def deregister_instance(
    self,
    service_name: str,
    ip: str,
    port: int
) -> bool:
    """
    注销服务实例

    参数:
        service_name: 服务名称
        ip: 实例 IP
        port: 实例端口
    
    返回:
        是否注销成功
    """
```

## 获取服务实例列表

```python
async def get_instances(
    self,
    service_name: str,
    healthy_only: bool = True
) -> list[dict]:
    """
    获取服务实例列表

    参数:
        service_name: 服务名称
        healthy_only: 是否只返回健康实例，默认为 True
    
    返回:
        实例列表，每个实例包含以下字段：
        - ip: 实例 IP
        - port: 实例端口
        - metadata: 实例元数据
        - healthy: 是否健康
        - weight: 权重
        - enabled: 是否启用
    """
```

## 使用示例

```python
from use_nacos import NacosClient

client = NacosClient("http://localhost:8848")

# 注册服务实例
success = await client.register_instance(
    "user-service",
    "192.168.1.10",
    8080,
    metadata={
        "version": "1.0.0",
        "tags": ["prod"]
    }
)
print(f"注册服务: {'成功' if success else '失败'}")

# 获取服务实例列表
instances = await client.get_instances("user-service")
for instance in instances:
    print(f"实例: {instance['ip']}:{instance['port']}")
    print(f"健康状态: {'健康' if instance['healthy'] else '不健康'}")
    print(f"元数据: {instance['metadata']}")

# 注销服务实例
success = await client.deregister_instance(
    "user-service",
    "192.168.1.10",
    8080
)
print(f"注销服务: {'成功' if success else '失败'}")
```