from themessage_server.medium import auth as medium_auth


def test_get_auth_url():
    user_id = 'qwerty'
    url = medium_auth.get_auth_url(user_id)
    assert url is not None
