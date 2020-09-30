from sanic import Blueprint
from sanic.response import json
from sanic_openapi import doc
from sanic.exceptions import abort

from models import ExampleModel as docModel


def blueprint(example_model, results_logging_producer, auth_required):
    route = Blueprint('example-ml-api', strict_slashes=True)

    @route.get('/predict/<uid:string>')
    @doc.tag('predict')
    @doc.summary('get models')
    @doc.description('Returns prediction for given ID')
    @doc.produces(docModel, content_type='application/json')
    @auth_required
    async def interference(request, uid):
        result = example_model.resolve_model(uid)
        results_logging_producer.log_result(result)
        if not result:
            abort(404, f'No results for UID "{uid}"')
        return json(result, content_type='application/json; charset=utf-8')

    return route
