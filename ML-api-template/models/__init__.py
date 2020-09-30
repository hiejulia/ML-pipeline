from sanic_openapi import doc


class ExampleModel:
    """
    Example domain object documentation that is used in swagger definition
    """
    field_a = doc.Float(description="field a description")
    field_b = doc.Integer(description="field b description")
    field_c = doc.Date(description="field c description")
    field_d = doc.Boolean(description="field d description")
    field_e = doc.String(description="field e description")

    def _validation_schema(self):
        return {
            'field_a': {'type': 'float', 'required': True, 'empty': False},
            'field_b': {'type': 'int', 'required': True, 'empty': False},
            'field_c': {'type': 'str', 'required': True, 'empty': False},
            'field_d': {'type': 'bool', 'required': True, 'empty': False},
            'field_e': {'type': 'str', 'required': True, 'empty': False},
        }


MockExampleModel = {
    'field_a': 1.1,
    'field_b': 2,
    'field_c': "3",
    'field_d': True,
    'field_e': "eee"
}

