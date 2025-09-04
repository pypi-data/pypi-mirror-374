from confluent_kafka.admin import AdminClient, NewTopic


class KafkaTopicManager:

    def __init__(self, bootstrap_servers, username=None, password=None):
        self.bootstrap_servers = bootstrap_servers
        configuration = {"bootstrap.servers": bootstrap_servers}
        if username and password:
            configuration = {
                "bootstrap.servers": bootstrap_servers,
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': 'SCRAM-SHA-512',
                'sasl.username': username,
                'sasl.password': password,
            }
        self.client = AdminClient({
            **configuration
        })

    def wait_for_complete(self, future_dict):
        for f in future_dict:
            future_dict[f].result()

    def create_topic(self, topic_name: str, num_partitions=1, replication_factor=3):
        topics_list = [NewTopic(topic_name, num_partitions=num_partitions, replication_factor=replication_factor)]
        result = self.client.create_topics(topics_list)
        self.wait_for_complete(result)

    def create_topics(self, topic_names: [str], num_partitions=1, replication_factor=3):
        topics_list = [NewTopic(tn, num_partitions=num_partitions, replication_factor=replication_factor) for tn in
                       topic_names]
        result = self.client.create_topics(topics_list)
        self.wait_for_complete(result)

    def list_topics(self) -> [str]:
        return list(self.client.list_topics().topics.keys())

    def topic_exists(self, topic_name) -> bool:
        return self.client.list_topics().topics.get(topic_name) is not None

    def delete_topic(self, topic_name):
        result = self.client.delete_topics(topics=[topic_name])
        self.wait_for_complete(result)

    def delete_topics(self, topic_names):
        result = self.client.delete_topics(topics=topic_names)
        self.wait_for_complete(result)
