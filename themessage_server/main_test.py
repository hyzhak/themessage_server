from themessage_server import main


async def test_status_ok(test_client):
    client = await test_client(main.create_app())
    resp = await client.get('/')
    assert resp.status == 200
    text = await resp.text()
    assert '{"status": "ok"}' in text
