from sanic import exceptions
from base64 import b64encode
from functools import wraps


def init_basic_auth(username, password):
    token = str(b64encode(bytes(f'{username}:{password}', 'utf-8')), 'utf-8')

    def auth_required(handler=None):
        @wraps(handler)
        async def wrapper(request, *args, **kwargs):
            auth = request.headers.get("Authorization", None)

            if not auth or auth != f'Basic {token}':
                raise exceptions.Unauthorized("Auth required.", scheme="Basic", realm="Restricted Area")

            return await handler(request, *args, **kwargs)

        return wrapper

    return auth_required
