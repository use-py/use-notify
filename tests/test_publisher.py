import pytest
from usepy_plugin_notify.notification import Publisher, Notify


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
    assert hasattr(notify, 'add')
    assert hasattr(notify, 'publish')


class MockChannel:
    def __init__(self):
        self.sent_message = None

    def send(self, message):
        self.sent_message = message

    async def send_async(self, message):
        self.sent_message = message
