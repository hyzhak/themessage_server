import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

from aiohttp import web
import os
from themessage_server import blueprint, medium_controller

main_blueprint = blueprint.Blueprint('main', 'main')
main_blueprint.register_blueprint(medium_controller.medium_blueprint, url_prefix='/medium')


@web.middleware
async def version_middleware(request, handler):
    resp = await handler(request)
    # TODO: should get from themessage_server.__version__
    resp.headers['X-VERSION'] = '0.0.1'
    return resp


@main_blueprint.get('/')
def root_router(request):
    return {'status': 'ok'}


def create_app():
    app = web.Application(middlewares=[
        version_middleware,
    ])
    main_blueprint.register_app(app)
    return app


def main():
    port_string = os.environ.get('SERVER_PORT', os.environ.get('PORT', None))
    port = int(port_string) if port_string else None
    app = create_app()
    web.run_app(app,
                host=os.environ.get('SERVER_IP', '0.0.0.0'),
                port=port)


if __name__ == '__main__':
    main()
