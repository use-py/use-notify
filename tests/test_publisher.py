import pytest

from use_notify.notification import NotificationPublishError, Notify, Publisher


@pytest.fixture
def publisher():
    return Publisher()


@pytest.fixture
def notify():
    return Notify()


def test_publisher_add(publisher):
    channel1 = MockChannel()
    channel2 = MockChannel()
    publisher.add(channel1, channel2)
    assert len(publisher.channels) == 2


def test_publisher_publish(publisher):
    channel = MockChannel()
    publisher.add(channel)
    publisher.publish("Test message")
    assert channel.sent_message == "Test message"


def test_notify_inherits_publisher_methods(notify):
    assert hasattr(notify, "add")
    assert hasattr(notify, "publish")


def test_publisher_retries_until_success():
    channel = FlakyChannel(failures_before_success=1, error_factory=TimeoutError)
    publisher = Publisher([channel], max_retries=1)

    publisher.publish("Test message")

    assert channel.attempts == 2
    assert channel.sent_message == "Test message"


def test_publisher_retries_other_channels_before_raising():
    failing_channel = FlakyChannel(failures_before_success=2, error_factory=TimeoutError)
    healthy_channel = MockChannel()
    publisher = Publisher(
        [failing_channel, healthy_channel],
        max_retries=1,
    )

    with pytest.raises(TimeoutError, match="send failed"):
        publisher.publish("Test message")

    assert failing_channel.attempts == 2
    assert healthy_channel.sent_message == "Test message"


@pytest.mark.asyncio
async def test_publisher_publish_async_retries_until_success():
    channel = AsyncFlakyChannel(failures_before_success=1, error_factory=TimeoutError)
    publisher = Publisher([channel], max_retries=1)

    await publisher.publish_async("Test message")

    assert channel.attempts == 2
    assert channel.sent_message == "Test message"


def test_publisher_raises_aggregated_error_for_multiple_failures():
    publisher = Publisher(
        [
            FlakyChannel(failures_before_success=3, error_factory=TimeoutError),
            FlakyChannel(failures_before_success=3, error_factory=TimeoutError),
        ],
        max_retries=1,
    )

    with pytest.raises(NotificationPublishError) as error_info:
        publisher.publish("Test message")

    assert len(error_info.value.failures) == 2
    assert "FlakyChannel" in str(error_info.value)


def test_publisher_does_not_retry_non_retriable_exception():
    channel = FlakyChannel(failures_before_success=3, error_factory=ValueError)
    publisher = Publisher([channel], max_retries=2)

    with pytest.raises(ValueError, match="send failed"):
        publisher.publish("Test message")

    assert channel.attempts == 1


def test_configure_retry_returns_same_publisher():
    publisher = Publisher()

    configured = publisher.configure_retry(max_retries=2)

    assert configured is publisher


class MockChannel:
    def __init__(self):
        self.sent_message = None

    def send(self, message):
        self.sent_message = message

    async def send_async(self, message):
        self.sent_message = message


class FlakyChannel(MockChannel):
    def __init__(self, failures_before_success, error_factory=RuntimeError):
        super().__init__()
        self.failures_before_success = failures_before_success
        self.error_factory = error_factory
        self.attempts = 0

    def send(self, message):
        self.attempts += 1
        if self.attempts <= self.failures_before_success:
            raise self.error_factory("send failed")
        self.sent_message = message


class AsyncFlakyChannel(MockChannel):
    def __init__(self, failures_before_success, error_factory=RuntimeError):
        super().__init__()
        self.failures_before_success = failures_before_success
        self.error_factory = error_factory
        self.attempts = 0

    async def send_async(self, message):
        self.attempts += 1
        if self.attempts <= self.failures_before_success:
            raise self.error_factory("send failed")
        self.sent_message = message
