import os
import logging
from confluent_kafka import Producer
from json import dumps


class ResultsProducer(Producer):
    """
    Encapsulation of kafka integration for prediction results gathering.
    """

    def __init__(self, group_id, kafka_broker_servers, results_topic, logger=logging):
        super().__init__({
            'bootstrap.servers': kafka_broker_servers,
            'metadata.broker.list': kafka_broker_servers,
            'group.id': group_id,
            'security.protocol': os.environ.get('LOG_SECURITY_PROTOCOL'),
            'ssl.ca.location': os.environ.get('LOG_SSL_CA_LOCATION'),
            'ssl.certificate.location': os.environ.get('LOG_SSL_CERT_LOCATION'),
            'ssl.key.location': os.environ.get('LOG_SSL_KEY_LOCATION'),
            'ssl.key.password': os.environ.get('LOG_SSL_KEY_PASSWORD')
        })
        self.results_topic = results_topic
        self.logger = logger

    def log_result(self, value):
        """
        Push value into results logging topic.

        :param value: JSON serializable object. None values are ignored.
        :raises Exception if value is not serializable
        """
        if not value:
            self.logger.warning('no results to be logged')
            return
        self.produce(topic=self.results_topic, value=dumps(value))
        self.flush(1)


class MockResultsProducer(ResultsProducer):
    """
    Local development mock for Kafka integration, logs all events that would be pushed into topic.
    """

    def __init__(self, group_id, kafka_broker_servers, results_topic, logger=logging):
        self.results_topic = results_topic
        self.logger = logger
        self.logger.info('MockResultsProducer in use.')

    def log_result(self, value):
        if not value:
            self.logger.warning('no results to be logged')
            return
        self.logger.debug(f'MockResultsProducer: flush topic {self.results_topic} event {dumps(value)}')
