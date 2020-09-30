
class ExampleModel:

    def __init__(self, redis):
        self.redis = redis

    def resolve_model(self, id):
        model = self.redis.fetch_all(id)
        if model is None:
            return None
        return model

    def update_model(self, records):
        self.redisd.update_hashset_values(records, lambda obj: obj['field_b'])
