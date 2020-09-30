from sanic import Blueprint
from sanic.response import json
from sanic_openapi import doc
from models import ExampleModel as docModel


def blueprint(example_model, auth_required):
    route = Blueprint('update', strict_slashes=True)

    @route.post('')
    @doc.description('Upload model')
    @doc.consumes(docModel, location='body', content_type='application/json')
    @auth_required
    async def update_predictions(request):
        records = request.json
        example_model.update_model(records)
        return json({'message': 'successfully updated'})

    return route
