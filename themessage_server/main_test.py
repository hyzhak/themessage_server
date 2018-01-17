import themessage_server
from themessage_server import main


async def test_status_ok(test_client):
    client = await test_client(main.create_app())
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert '{"status": "ok"}' in text


async def test_every_response_should_have_version_header(test_client):
    client = await test_client(main.create_app())
    resp = await client.get('/')
    assert resp.status == 200
    assert resp.headers.get('X-VERSION') == themessage_server.__version__
