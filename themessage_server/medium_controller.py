import logging

logger = logging.getLogger(__name__)

# TODO:
# may require fix https://pyjwt.readthedocs.io/en/latest/installation.html#legacy-dependencies
# because google app engine doesn't allow to compile C
import jwt
import os
from themessage_server import blueprint, storage

from webargs import fields
from webargs.aiohttpparser import use_args

medium_blueprint = blueprint.Blueprint('medium', __name__)

code_subscriptions = []


@medium_blueprint.get('/debug')
def debug(request):
    return f'Currently {len(code_subscriptions)} subscriptions'


# should be able to handle:
# https://example.com/callback/medium?state={{state}}&code={{code}}
# https://example.com/callback/medium?error=access_denied
@medium_blueprint.get('/callback')
@use_args({
    'code': fields.Str(),
    'error': fields.Str(),
    'state': fields.Str(),
})
async def medium_callback(request, args):
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
    state = args.get('state')

    logger.info(f'get code {code}')

    try:
        payload = jwt.decode(state, os.environ.get('JWT_SECRET'), algorithms=['HS256'])
    except jwt.DecodeError as err:
        return log_error('get callback request with broken state argument',
                         err=err,
                         request_payload={
                             'code': code,
                             'state': state,
                         })

    user_id = payload['user_id']

    storage.store_code(state, code)

    logger.info(f'get code {code} of user {user_id}')

    # def notify():
    #     for sub in code_subscriptions[:]:
    #         sub.put({'code': code, 'state': state, 'user_id': user_id})
    #
    # gevent.spawn(notify)

    # we could ever this operation move to the client
    # and return code right a way
    #
    # try:
    #     token = medium_integration.authorize(request.args.get('code'))
    # except medium.MediumError as err:
    #     logger.error(f'Can not authorize user by code {code}', exc_info=True, extra={
    #         'data': {
    #             'request': {
    #                 'args': request.args,
    #             },
    #         },
    #     })
    #     abort(400)

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

    return {
        'status': 'ok',
        'code': code,
    }


@medium_blueprint.get('/code/<user_id>')
def code_stream(user_id):
    code_stream_endpoint_name = f'medium.{code_stream.__name__}'

    logger.info('client start listen its code', extra={
        'user': {
            'id': user_id,
        },
    })

    def gen():
        q = Queue()

        def on_disconnect(*args, **kwargs):
            if request.endpoint == code_stream_endpoint_name:
                logger.info('client disconnects from a stream without getting auth code', extra={
                    'user': {
                        'id': user_id,
                    },
                })
                # send None which will be consider as the end
                q.put(None)

        # start stream

        code_subscriptions.append(q)
        request_finished.connect(on_disconnect, __app)

        # stream

        try:
            while True:
                result = q.get()

                if result and result['user_id'] == user_id:
                    yield result['code']
                    logger.info('client receive auth code', extra={
                        'user': {
                            'id': user_id,
                        },
                    })
                    break

                if result is None:
                    break
        except GeneratorExit:
            logger.warning('have problem to send auth code to a client', extra={
                'user': {
                    'id': user_id,
                },
            })

        # stop stream

        logger.info('before stop stream')

        code_subscriptions.remove(q)
        request_finished.disconnect(on_disconnect, __app)

    return Response(gen(), mimetype="text/event-stream")
