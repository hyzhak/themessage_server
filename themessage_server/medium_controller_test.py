import asyncio
import jwt
import os
import pytest
from themessage_server import main

url_prefix = '/medium'


@pytest.fixture()
def app():
    return main.create_app()


@pytest.fixture()
def user_state(monkeypatch):
    monkeypatch.setitem(os.environ, 'JWT_SECRET', 'secret')
    return jwt.encode({'user_id': 1}, key=os.environ.get('JWT_SECRET')).decode('ascii')


@pytest.fixture()
def client_get(app, test_client):
    async def make_get(url, current_app=None):
        client = await test_client(current_app or app)
        return await client.get(url)

    return make_get


async def test_medium_auth(client_get):
    resp = await client_get(f'{url_prefix}/auth')
    assert resp.status == 200
    j = await resp.json()
    assert len(j.get('url')) > 0
    assert len(j.get('user_id')) > 0


async def test_medium_debug(client_get):
    resp = await client_get(f'{url_prefix}/debug')
    assert resp.status == 200
    text = await resp.text()
    assert 'Currently 0 subscriptions' in text


async def test_callback_should_validate_state_and_return_passed_code(client_get, monkeypatch, user_state):
    resp = await client_get(f'{url_prefix}/callback?code=1&state={user_state}')
    assert resp.status == 200
    assert await resp.json() == {'status': 'ok', 'code': '1'}


@pytest.mark.timeout(2000)
async def test_code_stream_receives_callback_code(app, client_get, user_state):
    async def get_code():
        resp = await client_get(
            f'{url_prefix}/code/1',
            app,
        )
        assert resp.status == 200
        assert 'data: 1' in await resp.text()

    async def set_callback():
        # /callback should shoot later than /code/1
        await asyncio.sleep(.1)
        resp = await client_get(
            f'{url_prefix}/callback?code=1&state=1',
            app,
        )
        assert resp.status == 200
        assert await resp.json() == {'status': 'ok', 'code': '1'}

    res = await asyncio.gather(
        get_code(),
        set_callback(),
    )

    assert res is not None
