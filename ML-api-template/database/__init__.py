import redis as r
import json


def serialize(obj):
    return json.dumps(obj)


def deserialize(obj_str):
    return json.loads(obj_str)


class RedisDatabase:
    """
        Datalake Redis usage preferred usage pattern. By default values into redis are serialized to JSON.
    """
    def __init__(self, batch_size, key_time_to_live, serialization=(serialize, deserialize), **kwargs):
        self.batch_size = batch_size
        self.key_time_to_live = key_time_to_live
        self.serialize, self.deserialize = serialization
        self.redis = r.StrictRedis(**kwargs)

    def exists(self, key):
        return self.redis.exists(key) > 0

    def fetch_value(self, key):
        """
        Fetch given value from the key.

        :param key: top level key
        :return: value in python object
        """
        if not key:
            return None
        raw_value = self.redis.get(key)
        if not raw_value:
            return None
        return self.deserialize(raw_value)

    def fetch(self, key, field):
        """
        Fetch given field from the key.

        :param key: top level key
        :param field: field in the underlying hash
        :return: value in python object
        """
        if not key:
            return None
        raw_value = self.redis.hget(key, field)
        if not raw_value:
            return None
        return self.deserialize(raw_value)

    def fetch_all(self, key):
        """
        Fetch all values from the key.

        :param key: key to be retrieved
        :return: dictionary of all keys and values in key
        """
        if not key:
            return None
        all_values = self.redis.hgetall(key)
        return {k.decode('utf-8'): self.deserialize(v) for k, v in all_values.items()}

    def update_values(self, records, key_fn, map_fn=lambda x: x):
        cnt = 0
        p = self.redis.pipeline()

        for row in records:
            p = self._update_command_value(row, key_fn, map_fn, p)
            cnt += 1
            if cnt % self.batch_size == 0:
                p.execute()
                p = self.redis.pipeline()

        p.execute()

    def update_hash_values(self, records, key_fn, hash_key_fn, map_fn=lambda x: x):
        """
        Updates hash values of the key in batch format. Values are serialized in JSON format.

        :param records: list of dictionaries
        :param key_fn: method that takes record and outputs key
        :param hash_key_fn: method that takes record and hash_key key
        :param map_fn: function to map record into stored object
        :return:
        """
        cnt = 0
        p = self.redis.pipeline()

        for row in records:
            p = self._update_command_hash_value(row, key_fn, hash_key_fn, map_fn, p)
            cnt += 1
            if cnt % self.batch_size == 0:
                p.execute()
                p = self.redis.pipeline()

        p.execute()

    def update_hashset_values(self, records, key_fn, map_fn=lambda x: x):
        """
        Stores records as hash into key produced by key_fn. Values are serialized in JSON format.

        :param records: list of dictionaries
        :param key_fn: method that takes record and outputs key
        :param map_fn: function to map record into stored object
        :return:
        """
        cnt = 0
        p = self.redis.pipeline()

        for row in records:
            p = self._update_command_hashset(row, key_fn, map_fn, p)
            cnt += 1
            if cnt % self.batch_size == 0:
                p.execute()
                p = self.redis.pipeline()

        p.execute()

    def _update_command_value(self, record, key_fn, map_fn, pipeline):
        key = key_fn(record)
        value = self.serialize(map_fn(record))
        pipeline.set(key, value)
        pipeline.expire(key, self.key_time_to_live)
        return pipeline

    def _update_command_hashset(self, record, key_fn, map_fn, pipeline):
        key = key_fn(record)
        value = self.serialize(map_fn(record))
        pipeline.hmset(key, value)
        pipeline.expire(key, self.key_time_to_live)
        return pipeline

    def _update_command_hash_value(self, record, key_fn, hash_key_fn, map_fn, pipeline):
        key = key_fn(record)
        hash_key = hash_key_fn(record)
        value = self.serialize(map_fn(record))
        pipeline.hset(key, hash_key, value)
        pipeline.expire(key, self.key_time_to_live)
        return pipeline
