import jwt
import os
import pytest
from themessage_server import main

url_prefix = '/medium'


@pytest.fixture()
def app():
    return main.create_app()


@pytest.fixture()
def app_get(app, test_client):
    async def make_get(url):
        client = await test_client(app)
        return await client.get(url)

    return make_get


async def test_medium_debug(app_get):
    resp = await app_get(f'{url_prefix}/debug')
    assert resp.status == 200
    text = await resp.text()
    assert 'Currently 0 subscriptions' in text


async def test_callback_should_validate_state_and_return_passed_code(app_get, monkeypatch):
    monkeypatch.setitem(os.environ, 'JWT_SECRET', 'secret')
    state = jwt.encode({'user_id': 1}, key=os.environ.get('JWT_SECRET')).decode('ascii')
    resp = await app_get(f'{url_prefix}/callback?code=1&state={state}')
    assert resp.status == 200
    assert await resp.json() == {'status': 'ok', 'code': '1'}
