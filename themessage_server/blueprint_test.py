from aiohttp import web
from themessage_server.blueprint import Blueprint


class MockAioHttpApp:
    def __init__(self):
        self._routes = []

    @property
    def router(self):
        return self

    def add_route(self, method, path, handler):
        self._routes.append({
            'handler': handler,
            'method': method,
            'path': path,
        })

    async def send_get(self):
        route = self._routes[0]
        return await route['handler']({})


async def test_response_body_with_status():
    mock_app = MockAioHttpApp()
    b = Blueprint()

    @b.get('/')
    def handler(req):
        return 'body', 200

    b.register_app(mock_app)

    res = await mock_app.send_get()

    assert type(res) == web.Response
    assert res.body._value == b'body'
    assert res.status == 200
