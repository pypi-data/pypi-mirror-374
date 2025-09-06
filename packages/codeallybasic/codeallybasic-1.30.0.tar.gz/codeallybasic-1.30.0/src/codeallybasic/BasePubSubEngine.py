
from typing import Any
from typing import Callable
from typing import NewType

from pubsub.core import Publisher

Topic = NewType('Topic', str)
MessageListener = Callable[..., Any]


class BasePubSubEngine:
    """
    Wrapper class to hide underlying implementation
    """
    def __init__(self):
        self._publisher: Publisher = Publisher()

    def _subscribe(self, topic: Topic, listener: MessageListener):
        """

        Args:
            topic:
            listener:   This is really a UserListener

            For this implementation I do want this detail to leak through:

            From the docs
            In the user domain, a listener is any callable, regardless of signature. The return value is ignored,
            i.e. the listener will be treated as though it is a Callable[..., None]. Also, the args, "...", must be
            consistent with the MDS of the topic to which listener is being subscribed.
        """
        self._publisher.subscribe(listener, topic)

    def _sendMessage(self, topic: Topic, **kwargs):

        self._publisher.sendMessage(topic, **kwargs)
