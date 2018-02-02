import logging

logger = logging.getLogger(__name__)

import jwt
import medium
import os

# Go to http://medium.com/me/applications to get your application_id and application_secret.
client = medium.Client(application_id=os.environ.get('MEDIUM_APP_ID'),
                       application_secret=os.environ.get('MEDIUM_APP_SECRET'))


def authorize(code):
    """
    get user access token by authorize code

    :param code:
    :return: token
    """
    # Exchange the authorization code for an access token (maybe jwt?).
    auth = client.exchange_authorization_code(code,
                                              os.environ.get('MEDIUM_APP_CALLBACK_URL'))

    return auth['access_token']


def get_url(user_id):
    """
    Build the URL where you can send the user to obtain
    an authorization code.
    Arbitrary text of your choosing, which we will repeat
    back to you to help you prevent request forgery.

    :param user_id:
    :return: url
    """

    user_jwt = jwt.encode({'user_id': user_id},
                          os.environ.get('JWT_SECRET'),
                          algorithm='HS256',
                          )

    return client.get_authorization_url(user_jwt,
                                        os.environ.get('MEDIUM_APP_CALLBACK_URL'),
                                        ['basicProfile', 'listPublications', 'publishPost',
                                         # Integrations are not permitted to request extended scope
                                         # from users without explicit prior permission from Medium.
                                         # Attempting to request these permissions through the standard
                                         # user authentication flow will result in an error if extended
                                         # scope has not been authorized for an integration.
                                         # 'uploadImage',
                                         ])
