from flask import abort, Blueprint, jsonify, request, Response
import logging
import medium
from themessage_server import medium_integration

logger = logging.getLogger(__name__)

medium_blueprint = Blueprint('medium', __name__)


# should be able to handle:
# https://example.com/callback/medium?state={{state}}&code={{code}}
# https://example.com/callback/medium?error=access_denied
@medium_blueprint.route('/callback')
def medium_callback():
    if not request or not request.args:
        logger.info('does not have args')
        abort(400)

    if 'error' in request.args:
        logger.error('get medium callback error', extra={
            'stack': True,
            'data': {
                'request': {
                    'args': request.args,
                },
            },
        })
        return Response('ok', status=200)

    if 'state' not in request.args or 'code' not in request.args:
        logger.error('get medium callback without state or code', extra={
            'stack': True,
            'data': {
                'request': {
                    'args': request.args,
                },
            },
        })
        return Response('ok', status=200)

    code = request.args.get('code')

    logger.info(f'get code {code}')

    # we could ever this operation move to the client
    # and return code right a way
    try:
        token = medium_integration.authorize(request.args.get('code'))
    except medium.MediumError as err:
        logger.error(f'Can not authorize user by code {code}', exc_info=True, extra={
            'data': {
                'request': {
                    'args': request.args,
                },
            },
        })
        abort(400)

    # user = medium_integration.get_user()
    # logger.info(f'user @{user.get("username")} is authorized')
    # logger.info(user)

    # send message back to client if it's listening us
    # or store token locally and return to client once it will come

    # logging.warning('TODO:should store user token!')
    #
    # logging.info('temporal scenario - publish article')
    # with open('examples/article.md') as f:
    #     article = f.read()
    #     post = medium_integration.publish(token,
    #                                       title='Markdown test',
    #                                       content=article)
    #
    # logging.info(f'post is published to {post["url"]}')

    return jsonify({
        'status': 'ok',
        'token': token,
    })
