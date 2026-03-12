# -*- coding: utf-8 -*-
import asyncio
import logging
import smtplib
import time
from dataclasses import dataclass
from threading import RLock
from typing import List, Optional, Tuple, Type, TypeVar

import httpx
from use_notify import channels as channels_models


logger = logging.getLogger(__name__)
RetriableExceptions = Tuple[Type[BaseException], ...]
DEFAULT_RETRIABLE_EXCEPTIONS: RetriableExceptions = (
    TimeoutError,
    ConnectionError,
    OSError,
)
PublisherT = TypeVar("PublisherT", bound="Publisher")


@dataclass(frozen=True)
class RetryConfig:
    """Notification retry policy."""

    max_retries: int = 0
    retry_delay: float = 0.0
    retry_backoff: float = 1.0
    retriable_exceptions: RetriableExceptions = DEFAULT_RETRIABLE_EXCEPTIONS

    def __post_init__(self):
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be >= 0")
        if self.retry_backoff <= 0:
            raise ValueError("retry_backoff must be > 0")
        invalid_exceptions = [
            exception_type
            for exception_type in self.retriable_exceptions
            if not isinstance(exception_type, type)
            or not issubclass(exception_type, BaseException)
        ]
        if invalid_exceptions:
            raise ValueError(
                "retriable_exceptions must only contain exception types"
            )


class NotificationPublishError(RuntimeError):
    """Raised after all channels exhaust their retries."""

    def __init__(self, failures: List[Tuple[str, Exception]]):
        self.failures = failures
        failure_summary = ", ".join(
            f"{channel_name}: {error}" for channel_name, error in failures
        )
        super().__init__(f"Failed to publish notification via: {failure_summary}")


class Publisher:
    """A class that publishes notifications to multiple channels."""

    def __init__(
        self,
        channels: Optional[List[channels_models.BaseChannel]] = None,
        max_retries: int = 0,
        retry_delay: float = 0.0,
        retry_backoff: float = 1.0,
        retriable_exceptions: RetriableExceptions = DEFAULT_RETRIABLE_EXCEPTIONS,
    ):
        if channels is None:
            channels = []
        self._state_lock = RLock()
        self.channels = tuple(channels)
        self.retry_config = RetryConfig(
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            retriable_exceptions=retriable_exceptions,
        )

    def add(self, *channels):
        """
        Add channels to the Publisher.

        Args:
            *channels: Variable number of BaseChannel objects.
        """
        if not channels:
            return
        with self._state_lock:
            self.channels = self.channels + tuple(channels)

    def configure_retry(
        self: PublisherT,
        max_retries: int = 0,
        retry_delay: float = 0.0,
        retry_backoff: float = 1.0,
        retriable_exceptions: RetriableExceptions = DEFAULT_RETRIABLE_EXCEPTIONS,
    ) -> PublisherT:
        """
        Update retry policy for subsequent sends.
        """
        retry_config = RetryConfig(
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_backoff=retry_backoff,
            retriable_exceptions=retriable_exceptions,
        )
        with self._state_lock:
            self.retry_config = retry_config
        return self

    def publish(self, *args, **kwargs):
        """
        Publish a notification to all channels.
        """
        channels, retry_config = self._snapshot_state()
        failures = []
        for channel in channels:
            try:
                self._send_with_retry(channel, retry_config, *args, **kwargs)
            except Exception as error:
                failures.append((self._channel_name(channel), error))

        if failures:
            self._raise_publish_error(failures)

    async def publish_async(self, *args, **kwargs):
        """
        Publish a notification asynchronously to all channels.
        """
        channels, retry_config = self._snapshot_state()
        tasks = [
            self._send_with_retry_async(channel, retry_config, *args, **kwargs)
            for channel in channels
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        failures = []
        for channel, result in zip(channels, results):
            if isinstance(result, Exception):
                failures.append((self._channel_name(channel), result))

        if failures:
            self._raise_publish_error(failures)

    def _snapshot_state(self):
        with self._state_lock:
            return self.channels, self.retry_config

    def _send_with_retry(self, channel, retry_config: RetryConfig, *args, **kwargs):
        max_attempts = retry_config.max_retries + 1
        delay = retry_config.retry_delay

        for attempt in range(1, max_attempts + 1):
            try:
                channel.send(*args, **kwargs)
                return
            except Exception as error:
                if attempt == max_attempts:
                    raise

                if not self._is_retriable_exception(error, retry_config):
                    logger.debug(
                        "Channel %s send failed with non-retriable %s: %s",
                        self._channel_name(channel),
                        error.__class__.__name__,
                        error,
                    )
                    raise

                self._log_retry(channel, attempt, error, delay, retry_config)
                if delay > 0:
                    time.sleep(delay)
                delay *= retry_config.retry_backoff

    async def _send_with_retry_async(
        self, channel, retry_config: RetryConfig, *args, **kwargs
    ):
        max_attempts = retry_config.max_retries + 1
        delay = retry_config.retry_delay

        for attempt in range(1, max_attempts + 1):
            try:
                await channel.send_async(*args, **kwargs)
                return
            except Exception as error:
                if attempt == max_attempts:
                    raise

                if not self._is_retriable_exception(error, retry_config):
                    logger.debug(
                        "Channel %s send failed with non-retriable %s: %s",
                        self._channel_name(channel),
                        error.__class__.__name__,
                        error,
                    )
                    raise

                self._log_retry(channel, attempt, error, delay, retry_config)
                if delay > 0:
                    await asyncio.sleep(delay)
                delay *= retry_config.retry_backoff

    @staticmethod
    def _channel_name(channel) -> str:
        return channel.__class__.__name__

    def _log_retry(
        self,
        channel,
        attempt: int,
        error: Exception,
        delay: float,
        retry_config: RetryConfig,
    ):
        logger.debug(
            "Channel %s send failed on attempt %s/%s with %s: %s. Retrying in %.2fs",
            self._channel_name(channel),
            attempt,
            retry_config.max_retries + 1,
            error.__class__.__name__,
            error,
            delay,
        )

    @staticmethod
    def _raise_publish_error(failures):
        if len(failures) == 1:
            raise failures[0][1]
        raise NotificationPublishError(failures)

    def _is_retriable_exception(
        self, error: Exception, retry_config: RetryConfig
    ) -> bool:
        if isinstance(error, httpx.HTTPStatusError):
            if error.response is None:
                return False
            status_code = error.response.status_code
            return status_code in (408, 429) or status_code >= 500

        if isinstance(error, httpx.RequestError):
            return True

        if isinstance(error, smtplib.SMTPAuthenticationError):
            return False

        if isinstance(error, smtplib.SMTPResponseException):
            return 400 <= error.smtp_code < 500

        return isinstance(error, retry_config.retriable_exceptions)


class Notify(Publisher):
    """A subclass of Publisher that represents a notification publisher."""

    @classmethod
    def from_settings(cls, settings: dict):
        """
        Create a Notify instance from a settings object.

        Args:
            settings: A settings object.
        Example:
            settings = {
            ...     "BARK": {"token": "your token"},
            ...     "DINGTALK": {"access_token": "your access token"},
            ... }
            notify = Notify.from_settings(settings)
            notify.publish(title="消息标题", content="消息正文")

        Returns:
            A Notify instance.
        """
        channels = []
        for channel, cfg in settings.items():
            # Try to get class by case-insensitive match
            channel_cls = None
            for cls_name in dir(channels_models):
                if cls_name.lower() == channel.lower():
                    channel_cls = getattr(channels_models, cls_name)
                    break
            if not channel_cls:
                raise ValueError(f"Unknown channel {channel}")
            channel = channel_cls(cfg)
            channels.append(channel)
        return cls(channels)
