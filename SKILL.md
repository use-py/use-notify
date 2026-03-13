---
name: use-notify
description: Help users integrate and troubleshoot the use-notify Python library. Use when asked about use-notify, @notify, NotificationPublishError, RetryConfig, default notify instances, custom notification channels, or any Bark/Ding/WeChat/WeCom/Email/Chanify/Feishu/Ntfy/PushDeer/PushOver notification setup.
---

# use-notify

Use this skill when the user wants to add notifications with `use-notify`, choose a channel, wire `@notify` into existing code, or debug delivery and retry behavior.

## What to read

- For first-time setup, quick snippets, or migration examples, read `skill-references/quickstart.md`.
- For provider-specific configuration, exact class names, and channel keys, read `skill-references/channels.md`.
- For retries, default-instance semantics, errors, and common pitfalls, read `skill-references/troubleshooting.md`.

Read only the references needed for the request.

## Workflow

1. Identify the integration style the user actually needs.
2. Generate code against the current public API in this repo.
3. Prefer the smallest working example that matches the user's stack.
4. Call out behavior that often surprises users, especially retries and error propagation.

## Integration defaults

- Prefer `@notify(...)` when the user wants notifications around function execution.
- Prefer `useNotify()` plus `.add(...)` and `.publish(...)` when the user wants ad hoc sends from scripts, jobs, or services.
- Prefer `useNotify.from_settings(settings)` when the user already has a configuration dict and wants minimal boilerplate.
- If the user does not name a real provider, use `useNotifyChannel.Console()` in examples so the snippet stays runnable without secrets.

## API guardrails

- Use exact exported names: `useNotify`, `useNotifyChannel`, `notify`, `NotificationPublishError`, `RetryConfig`.
- Use exact channel class names: `Bark`, `Chanify`, `Console`, `Ding`, `Email`, `Feishu`, `Ntfy`, `PushDeer`, `PushOver`, `WeChat`, `WeCom`.
- `WeCom` is an alias of `WeChat`.
- Custom channels must implement `send(content, title=None)` and `send_async(content, title=None)`.
- The decorator parameters are `notify_on_success` and `notify_on_error`, not older variants like `on_success` or `on_failure`.
- Do not suggest `notify_on_success=False` and `notify_on_error=False` together; current validation rejects that.
- Default notify instances are scoped to the current execution context, not a process-wide global singleton.

## Response guidance

- Keep examples copy-pasteable.
- When helping with failures, explain whether the user is calling the publisher API directly or using the decorator.
- When the request touches retries or delivery guarantees, explicitly mention how single-channel and multi-channel failures are surfaced.
