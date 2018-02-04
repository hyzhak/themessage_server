import logging

logger = logging.getLogger(__name__)

import aiohttp_sse
import asyncio
# TODO:
# may require fix https://pyjwt.readthedocs.io/en/latest/installation.html#legacy-dependencies
# because google app engine doesn't allow to compile C
import jwt
import os
import uuid
from webargs import fields
from webargs.aiohttpparser import use_args, use_kwargs

from themessage_server import blueprint, medium, storage
from themessage_server.medium import auth as medium_auth

medium_blueprint = blueprint.Blueprint('medium', __name__)

subscriptions = []


@medium_blueprint.get('/auth')
def auth(request):
    user_id = str(uuid.uuid1())
    secret = str(uuid.uuid1())
    url = medium_auth.get_auth_url(f'{user_id}_{secret}')
    return {
        'url': url,
        'user_id': user_id,
        'secret': secret,
    }


@medium_blueprint.get('/debug')
def debug(request):
    return f'Currently {len(subscriptions)} subscriptions'


@medium_blueprint.get('/callback')
@use_args({
    'code': fields.Str(),
    'error': fields.Str(),
    'state': fields.Str(),
})
async def medium_callback(request, args):
    """
    should be able to handle:
    https://example.com/callback/medium?state={{state}}&code={{code}}
    https://example.com/callback/medium?error=access_denied

    :param request:
    :param args:
    :return:
    """

    def log_error(msg, request_payload=None, err=None, code=400):
        request_payload = request_payload or {}
        logging_data = {
            'request': {
                'args': args,
            },
        }

        if request_payload:
            logging_data['request']['payload'] = request_payload

        if err:
            logging_data['error'] = err

        logger.error(msg, extra={
            'stack': True,
            'data': logging_data,
        })

        response_data = {
            'status': 'error',
            'message': msg,
        }
        if err:
            response_data['error'] = str(err)
        if request_payload:
            response_data['payload'] = request_payload
        return response_data, code

    if not args:
        return log_error('does not have args')

    if 'error' in args:
        return log_error('get medium callback error')

    if 'state' not in args or 'code' not in args:
        return log_error('get medium callback without state or code')

    code = args.get('code')
    logger.info(f'get code {code}')

    # state = args.get('state')
    # try:
    #     payload = jwt.decode(state, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
    # except jwt.DecodeError as err:
    #     return log_error('get callback request with broken state argument',
    #                      err=err,
    #                      request_payload={
    #                          'code': code,
    #                          'state': state,
    #                      })
    # user_id = payload['user_id']
    # storage.store_code(user_id, code)
    token = medium_auth.get_token(code)
    user_id = args.get('state')
    storage.store_token(user_id, token)

    logger.info(f'get code {code} of user {user_id}')

    return {
        'status': 'ok',
        'code': code,
    }


@medium_blueprint.get('/token/{user_id}')
@use_kwargs({
    'user_id': fields.Str(location='match_info'),
})
async def code_stream(request, user_id):
    logger.info(f'client {user_id} started listen its code', extra={
        'user': {
            'id': user_id,
        },
    })

    loop = request.app.loop

    subscriptions.append(user_id)

    try:

        async with aiohttp_sse.sse_response(request) as resp:
            while True:
                # TODO: it would be better to create callback/promise
                # which will be resolved once we would get the code
                await asyncio.sleep(1, loop=loop)
                token = storage.get_token(user_id)
                if token is not None:
                    logger.info(f'we got token {token} for {user_id}', extra={
                        'user': {
                            'id': user_id,
                        },
                    })
                    resp.send(token)
                    break
    except asyncio.CancelledError as e:
        logger.info(f'client {user_id} has cancelled request', extra={
            'user': {
                'id': user_id,
            },
        })
        subscriptions.remove(user_id)
        raise e

    subscriptions.remove(user_id)

    return resp
