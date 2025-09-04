class InvalidEventTopicException(Exception):
    pass


class InvalidEventStructure(Exception):
    pass


class InvalidEventModelForTopic(Exception):
    pass


class DelayQueueTopicNotSetException(Exception):
    pass


class InvalidProduceEventParameters(Exception):
    pass


class InvalidDelayEventParameters(Exception):
    pass