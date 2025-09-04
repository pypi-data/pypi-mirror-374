import asyncio
import signal


class KafkaClientGracefulKiller:

    def __init__(self, client):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.client = client

    def exit_gracefully(self, signum, frame):
        print("Gracefully killing kafka client <3")
        asyncio.create_task(self.client.stop())
