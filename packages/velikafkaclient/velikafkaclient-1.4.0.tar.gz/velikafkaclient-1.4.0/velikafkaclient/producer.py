import json
import time

from confluent_kafka import Producer

from .exceptions import DelayQueueTopicNotSetException, InvalidProduceEventParameters, InvalidDelayEventParameters
from .constants import DelayEventParam


class KafkaEventProducer:
    """
        Constructor Parameters:
            bootstrap_servers (str): kafka server urls, separated by ";"
            delay_queue_topic: (str): topic name for a "delay queue"
            app_dedicated_topic: (str): topic name for events which come out of the "delay queue" (a dedicated topic
            for the app to process event after it's been in a "delay queue"
    """

    def __init__(self, bootstrap_servers, delay_queue_topic: str = None, app_dedicated_topic: str = None, username=None,
                 password=None):
        self.delay_queue_topic = delay_queue_topic
        self.app_dedicated_topic = app_dedicated_topic
        configuration = {'bootstrap.servers': bootstrap_servers,
                         'acks': 'all'
                         }
        if username and password:
            auth_creds = {
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': 'SCRAM-SHA-512',
                'sasl.username': username,
                'sasl.password': password,
            }
            configuration = {**configuration, **auth_creds}

        self.producer = Producer(configuration)

    def produce_event(self, topic_name: str, event_data: dict, key: str = None):
        if not topic_name or not event_data:
            raise InvalidProduceEventParameters(f"topic_name: {topic_name}, event_data: {event_data} ")
        json_data = json.dumps(event_data).encode()
        self.producer.produce(topic_name, json_data, key=key)

    def delay_event(self, original_topic: str, event_data: dict):
        if not self.delay_queue_topic:
            raise DelayQueueTopicNotSetException()

        if not original_topic or not event_data:
            raise InvalidDelayEventParameters(f"original_topic: {original_topic}, event_data: {event_data}")

        # Set variables for "delay queue"
        event_data[DelayEventParam.DELAY_COUNT.value] = event_data.get(DelayEventParam.DELAY_COUNT.value, 0) + 1
        event_data[DelayEventParam.INIT_TIME.value] = time.time()
        event_data[DelayEventParam.SOURCE_TOPIC.value] = self.app_dedicated_topic
        event_data[DelayEventParam.ORIGINAL_TOPIC.value] = event_data.get(DelayEventParam.ORIGINAL_TOPIC.value,
                                                                          original_topic)

        self.produce_event(self.delay_queue_topic, event_data)

    def flush(self, timeout=3):
        # TODO max retries ?
        messages_left = -1
        while messages_left != 0:
            messages_left = self.producer.flush(timeout)
        return self.producer.flush(timeout)
