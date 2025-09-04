from enum import Enum


class DelayEventParam(Enum):
    # How many times has event been dropped to a delay queue
    DELAY_COUNT = 'delay_count'

    # When was the event last dropped to the delay queue
    INIT_TIME = 'init_time'

    # To which topic should the event be sent after delay
    SOURCE_TOPIC = 'source_topic'

    # From which topic was this event consumed originally
    ORIGINAL_TOPIC = 'original_topic'
