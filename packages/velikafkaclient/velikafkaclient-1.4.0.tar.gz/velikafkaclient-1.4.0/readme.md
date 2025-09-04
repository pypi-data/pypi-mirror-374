### Kafka Client for VELI.STORE

### Description

This module is used for producing kafka events, subscribing to kafka topics and consuming kafka events.

### To remember:
Each kafka topic event has a predefined structure which you can see in `velikafkaclient/eventregistration`, producer 
and consumer both have built in validation, meaning that if incorrect object structure is sent to a topic then producer 
will raise an exception as well as consumer.


### How to use Producer/Consumer:

* Initialize kafka producer:

```python
BOOTSTRAP_SERVERS = "kafka bootstrap servers uri"
kafka_producer: AsyncKafkaEventProducer = AsyncKafkaEventProducer(BOOTSTRAP_SERVERS)
await kafka_producer.start()
```

* Produce events to a topic:

```python
from events.base import KafkaEvent
from topics.base import BaseTopic

kafka_event = KafkaEvent()
await kafka_producer.produce_event(BaseTopic, kafka_event)
```

* Setup and start consumer

```python
async def base_handler(kafka_event: KafkaEvent):
    print(str(kafka_event))
    
    
bootstrap_servers = BOOTSTRAP_SERVER
consumer = AsyncKafkaConsumer(bootstrap_servers, group_id=GROUP_ID)
consumer.subscribe(BaseTopic, base_handler)

await consumer.start()
await consumer.consume()
```


### How to add topics:
To add a new topic you need three things:
 1. Topic itself
 2. Topic event structure
 3. Register Event structure to a Topic 

All changes are done in `velikafkaclient` library (in the `veli_libs` repo)

* To add a topic go to `kafka-client/velikafkaclient/topics` and add topic like this:
```python
class SomeTopicCollection(KafkaTopic):
    
    USER_REGISTRATIONS = 'user_registrations'
```

* To add an event structure go to `kafka-client/velikafkaclient/events` and create pydantic model for event structure:
```python
class UserRegistrationEvent(KafkaEvent):
    
    id: int
    username: str
    password: str
    username: str
```

* To register event structure to a topic go to `kafka-client/velikafkaclient/eventregistration.py` and add:
```python
kafka_topic_events.register_topic_event_model(KafkaTopic.USER_REGISTRATIONS, UserRegistrationEvent)
```

Once done follow the instructions in the `veli_libs` readme to update the library on `pyip`


### How to manage topics with TopicManager:

```python
from velikafkaclient.topicmanager import KafkaTopicManager

client = KafkaTopicManager(BOOTSTRAP_SERVERS)


# Create Topic
client.create_topic('topic_name')


# Create Multiple Topics
topics = ['topic_name_1', 'topic_name_2']
client.create_topics(topics)


# List Topics
print(client.list_topics())


# Delete Topic
client.delete_topic('topic_name')


# Delete Multiple Topics
topics = ['topic_name_1', 'topic_name_2']
client.delete_topics(topics)


# Check if topic exists
print(client.topic_exists('topic_name'))

```