# Channels

Use exact class names from `useNotifyChannel`.

## Channel list

- `Bark`
- `Chanify`
- `Console`
- `Ding`
- `Email`
- `Feishu`
- `Ntfy`
- `PushDeer`
- `PushOver`
- `WeChat`
- `WeCom` as an alias of `WeChat`

## Minimal examples

### Bark

```python
useNotifyChannel.Bark(
    {
        "token": "your_bark_token",
        "base_url": "https://api.day.app",
        "badge": 1,
        "sound": "bell",
        "icon": "https://example.com/icon.png",
        "group": "ops",
        "url": "https://example.com",
    }
)
```

### Ding

```python
useNotifyChannel.Ding(
    {
        "token": "your_ding_token",
        "at_all": False,
        "at_mobiles": ["13800000000"],
        "at_user_ids": ["user-1"],
    }
)
```

### WeChat / WeCom

```python
useNotifyChannel.WeChat(
    {
        "token": "your_wechat_key",
        "mentioned_list": ["@all"],
        "mentioned_mobile_list": ["13800000000"],
    }
)
```

### Email

```python
useNotifyChannel.Email(
    {
        "server": "smtp.gmail.com",
        "port": 465,
        "username": "bot@example.com",
        "password": "app-password",
        "from_email": "bot@example.com",
        "to_emails": ["ops@example.com"],
        "use_ssl": True,
        "use_tls": False,
    }
)
```

For port `465`, SSL is used by default. For port `587`, STARTTLS is used by
default unless `use_ssl` or `use_tls` is set explicitly.

### Chanify

```python
useNotifyChannel.Chanify(
    {
        "token": "your_chanify_token",
        "base_url": "https://api.chanify.net",
    }
)
```

### Feishu

```python
useNotifyChannel.Feishu(
    {
        "token": "your_feishu_token",
        "at_all": True,
        "at_user_ids": ["ou_xxx"],
    }
)
```

### Ntfy

```python
useNotifyChannel.Ntfy(
    {
        "topic": "alerts",
        "base_url": "https://ntfy.sh",
        "priority": 4,
        "tags": ["warning"],
        "click": "https://example.com",
        "attach": "https://example.com/file.txt",
        "actions": [
            {"action": "view", "label": "Open", "url": "https://example.com"}
        ],
    }
)
```

### PushDeer

```python
useNotifyChannel.PushDeer(
    {
        "token": "your_pushkey",
        "base_url": "https://api2.pushdeer.com",
        "type": "markdown",
    }
)
```

### PushOver

```python
useNotifyChannel.PushOver(
    {
        "token": "your_app_token",
        "user": "your_user_key",
    }
)
```

### Console

```python
useNotifyChannel.Console()
```

## Naming pitfalls

- Use `PushDeer`, not `Pushdeer`.
- Use `PushOver`, not `Pushover`.
- Use `WeChat` or `WeCom`; both resolve to the same implementation.
- Use `base_url` for Bark, Chanify, Ntfy, and PushDeer when pointing to self-hosted endpoints.

## Dynamic credentials

Credential fields can be static strings or zero-argument callables. The callable
is resolved when the channel builds the request, so application code can refresh
or cache credentials outside `use-notify`:

```python
useNotifyChannel.Bark({"token": lambda: get_current_bark_token()})
```

This library does not implement provider-specific OAuth refresh flows, background
refresh threads, or credential persistence. It only reads the current credential
value before sending.
