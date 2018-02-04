# for the moment we use very simple local in memory storage
# for auth token. But in future it is very likely that
# this project will migrate on something more distributed and stable
# (for example Redis)

storage = {}


def store_token(user_id, token):
    storage[str(user_id)] = token


def get_token(user_id):
    return storage.get(str(user_id))
