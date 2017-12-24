# for the moment we use very simple local in memory storage
# for auth code. But in future it is very likely that
# this project will migrate on something more distributed and stable

storage = {}


def store_code(user_id, code):
    storage[str(user_id)] = code


def get_code(user_id):
    return storage.get(str(user_id))
