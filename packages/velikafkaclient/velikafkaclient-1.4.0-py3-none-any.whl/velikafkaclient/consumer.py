import logging
import time

from confluent_kafka import Consumer, KafkaError, KafkaException


class RateLimit:
    batch_size: int = 1
    batch_waiting_time: int = 3
    units_per_minute: int = 10000

    def __init__(self, batch_size=1, batch_waiting_time=3, units_per_minute=10000):
        self.batch_size = batch_size
        self.batch_waiting_time = batch_waiting_time
        self.units_per_minute = units_per_minute


class Batch:

    def __init__(self):
        self.events = dict()

    def add(self, event):
        topic = event.topic()
        if topic not in self.events:
            self.events[topic] = []
        self.events[topic].append(event)

    def reset(self):
        self.events = dict()

    def size(self):
        res = 0
        for t in self.events:
            res += len(self.events[t])
        return res


class EventRate:
    processed_batch_count: int = 0
    batch = Batch()
    session_start_time = time.time()
    batch_session_start_time = time.time()


class KafkaConsumer:

    def __init__(self, bootstrap_servers, rate_limit: RateLimit = RateLimit(), group_id=None, auto_commit=True,
                 event_loop=None, username=None, password=None):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.subscriptions = dict()
        self.auto_commit = auto_commit
        configuration = {'bootstrap.servers': bootstrap_servers,
                         'group.id': group_id,
                         'auto.offset.reset': 'earliest',
                         'enable.auto.commit': auto_commit
                         }
        if username and password:
            auth_creds = {
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': 'SCRAM-SHA-512',
                'sasl.username': username,
                'sasl.password': password,
            }
            configuration = {**configuration, **auth_creds}
        self.consumer = Consumer(configuration)
        self.rate_limit = rate_limit
        self.event_rate = EventRate()
        self.event_loop = event_loop
        self.executor = self.execute
        if event_loop:
            self.executor = self.async_execute

    def subscribe(self, topic, handler):
        self.subscriptions[topic] = handler

    def start(self):
        self.consumer.subscribe(list(self.subscriptions.keys()))

        try:
            while True:
                event = self.consumer.poll(timeout=1.0)
                time_now = time.time()
                batch_time_lapse = time_now - self.event_rate.batch_session_start_time

                if event is None:
                    if batch_time_lapse >= self.rate_limit.batch_waiting_time:
                        self.process_events(time_now)
                    continue

                if event.error():
                    if event.error().code() == KafkaError._PARTITION_EOF:
                        logging.info('%% %s [%d] reached end at offset %d\n' %
                                     (event.topic(), event.partition(), event.offset()))
                    elif event.error():
                        # TODO what to do ?
                        raise KafkaException(event.error())
                else:

                    self.event_rate.batch.add(event)

                    if batch_time_lapse >= self.rate_limit.batch_waiting_time or self.event_rate.batch.size() >= self.rate_limit.batch_size:
                        self.process_events(time_now)

                    time_lapse = time_now - self.event_rate.session_start_time
                    if time_lapse >= 60:
                        self.event_rate.processed_batch_count = 0
                        self.event_rate.session_start_time = time_now
                    else:
                        if self.event_rate.processed_batch_count >= self.rate_limit.units_per_minute:
                            time.sleep(60 - time_lapse + 10)
                            self.event_rate.batch_session_start_time = time.time()
                            continue

        finally:
            self.consumer.close()

    def stop(self):
        self.consumer.close()

    def process_events(self, time_now):
        try:
            for topic in self.event_rate.batch.events:
                self.executor(topic)

            if not self.auto_commit:
                self.consumer.commit()

            self.event_rate.batch_session_start_time = time_now
            self.event_rate.processed_batch_count += 1
            self.event_rate.batch.reset()
        except Exception as e:
            # TODO implement
            raise e

    def commit(self):
        self.consumer.commit()

    def execute(self, topic):
        self.subscriptions[topic](self.event_rate.batch.events[topic])

    def async_execute(self, topic):
        self.event_loop.run_until_complete(self.subscriptions[topic](self.event_rate.batch.events[topic]))
