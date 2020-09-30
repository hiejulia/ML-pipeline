import os
from datetime import timedelta
from sanic import Sanic
from sanic.log import logger
from sanic_json_logging import setup_json_logging
from sanic_openapi import swagger_blueprint
from sanic_prometheus import monitor

from basic_auth import init_basic_auth as basic_auth_filter
from database import RedisDatabase
from models.accessors import ExampleModel
from routes.predictions import blueprint as api
from routes.update import blueprint as update_api
from routes.health_checks import blueprint as health_checks

environment = os.environ.get('API_ENVIRONMENT', 'LOCAL_DEV')
if environment == 'LOCAL_DEV':
    from result_logging.kafka import MockResultsProducer as ResultsProducer
else:
    from result_logging.kafka import ResultsProducer

host_endpoint = os.environ.get('API_GATEWAY_HOST', 'localhost:5002')
api_basepath = '/example-ml-api'

app = Sanic("example-ml-api", strict_slashes=True)
if environment != 'LOCAL_DEV':
    setup_json_logging(app)

app.config.API_VERSION = '0.0.1'
app.config.API_TITLE = 'Example API'
app.config.API_DESCRIPTION = 'Example API description, this will be shown into Live documenation top panel.'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json; charset=utf-8']
app.config.API_HOST = host_endpoint
app.config.API_BASEPATH = ''
app.config.API_SCHEMES = ['http'] if environment == 'LOCAL_DEV' else ['https']
app.config.API_SECURITY_DEFINITIONS = {
    'basicAuth': {
        'type': 'basic',
        'description': 'Credentials can be queried from datalake team'
    }
}
app.config.API_SECURITY = [
    {
        'basicAuth': []
    }
]

auth_required = basic_auth_filter(
    username=os.environ.get('BASIC_AUTH_READ_USERNAME', 'local-read'),
    password=os.environ.get('BASIC_AUTH_READ_PASSWORD', 'local-read-pw')
)

auth_required_update = basic_auth_filter(
    username=os.environ.get('BASIC_AUTH_UPDATE_USERNAME', 'local-update'),
    password=os.environ.get('BASIC_AUTH_UPDATE_PASSWORD', 'local-update-pw')
)

redis = RedisDatabase(
    host=os.environ.get('EXAMPLE_ML_API_DB_SERVICE_HOST', 'localhost'),
    port=int(os.environ.get('EXAMPLE_ML_API_DB_SERVICE_PORT', '6379')),
    password=os.environ.get('EXAMPLE_ML_API_DB_DATABASE_PASSWORD'),
    retry_on_timeout=True,
    batch_size=int(os.environ.get('REDIS_PIPELINE_BATCH_SIZE', 100)),
    key_time_to_live=timedelta(days=int(os.environ.get('KEY_TIME_TO_LIVE_DAYS', 15)))
)

"""
Model
"""

model = ExampleModel(redis)

kafka_brokers = os.environ.get('KAFKA_BROKERS', 'localhost:9092')
kafka_topic = os.environ.get('LOG_RESULTS_LOG_TOPIC', 'ml-api-template-results')

results_logging_producer = ResultsProducer('ml-api-template-result-logger', kafka_brokers, kafka_topic, logger)

predict_api = api(model, results_logging_producer, auth_required)
update_api = update_api(model, auth_required_update)

app.blueprint(swagger_blueprint, url_prefix=f'{api_basepath}/v1/api-docs')
app.blueprint(predict_api, url_prefix=f'{api_basepath}/v1')
app.blueprint(update_api, url_prefix=f'{api_basepath}/v1/update')
app.blueprint(health_checks(), url_prefix='/health')

if __name__ == '__main__':
    monitor(app).expose_endpoint()
    app.run(host='0.0.0.0', port=5002, workers=2)
