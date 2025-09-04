from aiokafka import AIOKafkaConsumer


class AsyncKafkaConsumer:

    def __init__(self, bootstrap_servers, group_id=None, auto_commit=True):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.subscriptions = dict()
        self.auto_commit = auto_commit
        self.consumer = None

    def subscribe(self, topic, handler):
        self.subscriptions[topic] = handler

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            *list(self.subscriptions.keys()),
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            enable_auto_commit=self.auto_commit
        )
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                await self.subscriptions[msg.topic](msg.topic, msg.value)
                # TODO implement commit
        finally:
            await self.consumer.stop()
