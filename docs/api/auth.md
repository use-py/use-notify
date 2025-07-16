# 认证配置

use-notify 支持多种认证方式，包括用户名密码认证和 TLS 证书认证。

## 用户名密码认证

最简单的认证方式是使用用户名和密码：

```python
from use_nacos import NacosClient

client = NacosClient(
    server_addresses="http://localhost:8848",
    username="nacos",
    password="nacos"
)
```

## TLS 证书认证

对于需要更高安全性的环境，use-notify 支持 TLS 证书认证：

```python
client = NacosClient(
    server_addresses="https://localhost:8848",
    tls_enabled=True,
    ca_file="/path/to/ca.pem",
    cert_file="/path/to/client-cert.pem",
    key_file="/path/to/client-key.pem"
)
```

### TLS 配置说明

- `ca_file`: CA 证书文件路径，用于验证服务器证书
- `cert_file`: 客户端证书文件路径
- `key_file`: 客户端私钥文件路径

## 最佳实践

1. 在生产环境中始终启用认证
2. 使用环境变量管理认证信息
3. 定期更新密码和证书
4. 使用专用服务账号
5. 避免在代码中硬编码认证信息

```python
import os
from use_nacos import NacosClient

# 从环境变量获取认证信息
client = NacosClient(
    server_addresses=os.getenv("NACOS_SERVER"),
    username=os.getenv("NACOS_USERNAME"),
    password=os.getenv("NACOS_PASSWORD")
)
```

## 错误处理

```python
from use_nacos.exceptions import NacosAuthException

try:
    client = NacosClient(
        server_addresses="http://localhost:8848",
        username="wrong_user",
        password="wrong_pass"
    )
    await client.get_config("app.yaml")
except NacosAuthException as e:
    print(f"认证失败: {e}")
```
