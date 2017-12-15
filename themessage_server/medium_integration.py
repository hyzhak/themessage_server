import logging

logger = logging.getLogger(__name__)

import medium
import os

# Go to http://medium.com/me/applications to get your application_id and application_secret.
client = medium.Client(application_id=os.environ.get('MEDIUM_APP_ID'),
                       application_secret=os.environ.get('MEDIUM_APP_SECRET'))


def authorize(code):
    # Exchange the authorization code for an access token (maybe jwt?).
    auth = client.exchange_authorization_code(code,
                                              os.environ.get('MEDIUM_APP_CALLBACK_URL'))

    return auth['access_token']


def get_url(secret_status='qwerty'):
    # Build the URL where you can send the user to obtain an authorization code.
    # Arbitrary text of your choosing, which we will repeat back to you to help you prevent request forgery.

    return client.get_authorization_url(secret_status,
                                        os.environ.get('MEDIUM_APP_CALLBACK_URL'),
                                        ['basicProfile', 'listPublications', 'publishPost',
                                         # Integrations are not permitted to request extended scope
                                         # from users without explicit prior permission from Medium.
                                         # Attempting to request these permissions through the standard
                                         # user authentication flow will result in an error if extended
                                         # scope has not been authorized for an integration.
                                         # 'uploadImage',
                                         ])


def get_user(token=None):
    """
    Get profile details of the user identified by the access token.

    :param token:
    :return:
    """
    if token:
        client.access_token = token

    return client.get_current_user()


def publish(token,
            title, content,
            content_format='markdown',
            publish_status='draft'):
    client.access_token = token
    # Get profile details of the user identified by the access token.
    user = client.get_current_user()

    # Create a draft post.
    return client.create_post(user['id'],
                              title,
                              content,
                              content_format,
                              publish_status=publish_status,
                              )
