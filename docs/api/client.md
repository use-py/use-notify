# NacosClient API

`NacosClient` 是 use-notify 的核心类，提供了与 Nacos 服务器交互的所有基本功能。

## 构造函数

```python
def __init__(
    server_addresses: str | list[str],
    namespace: str = "public",
    username: str | None = None,
    password: str | None = None,
    timeout: int = 3,
    tls_enabled: bool = False,
    ca_file: str | None = None,
    cert_file: str | None = None,
    key_file: str | None = None,
):
```

### 参数说明

- `server_addresses`: Nacos 服务器地址，可以是单个地址字符串或地址列表
- `namespace`: 命名空间 ID，默认为 "public"
- `username`: 认证用户名（可选）
- `password`: 认证密码（可选）
- `timeout`: 请求超时时间，单位为秒，默认为 3 秒
- `tls_enabled`: 是否启用 TLS 加密，默认为 False
- `ca_file`: CA 证书文件路径（可选）
- `cert_file`: 客户端证书文件路径（可选）
- `key_file`: 客户端私钥文件路径（可选）

## 基本用法

```python
from use_nacos import NacosClient

# 创建客户端实例
client = NacosClient(
    server_addresses="http://localhost:8848",
    namespace="public"
)

# 使用认证
client_with_auth = NacosClient(
    server_addresses="http://localhost:8848",
    namespace="public",
    username="nacos",
    password="nacos"
)

# 使用 TLS
client_with_tls = NacosClient(
    server_addresses="https://localhost:8848",
    tls_enabled=True,
    ca_file="/path/to/ca.pem",
    cert_file="/path/to/client-cert.pem",
    key_file="/path/to/client-key.pem"
)
```

## 错误处理

客户端操作可能抛出以下异常：

- `NacosConnectionError`: 连接 Nacos 服务器失败
- `NacosAuthException`: 认证失败
- `NacosRequestException`: 请求处理失败

```python
try:
    client = NacosClient(server_addresses="http://localhost:8848")
    await client.get_config("app.yaml", "DEFAULT_GROUP")
except NacosConnectionError as e:
    print(f"连接失败: {e}")
except NacosAuthException as e:
    print(f"认证失败: {e}")
except NacosRequestException as e:
    print(f"请求失败: {e}")
```
