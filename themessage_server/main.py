import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

from gevent.pywsgi import WSGIServer

from flask import Flask, jsonify
import os
from themessage_server import medium_controller

app = Flask(__name__)

app.register_blueprint(medium_controller.medium_blueprint, url_prefix='/medium')
medium_controller.set_app(app)


@app.route('/')
def root_router():
    return jsonify({'status': 'ok'})


def main():
    port_string = os.environ.get('SERVER_PORT', None)
    port = int(port_string) if port_string else None

    # TODO: 1) gunicorn 2) uwsgi

    #
    # gevent WSGI Server
    #

    # app.debug = True
    server = WSGIServer(
        (os.environ.get('SERVER_IP', '0.0.0.0'), port),
        app)
    server.serve_forever()

    #
    # flask built-in server
    #

    # app.run(host=os.environ.get('SERVER_IP', '0.0.0.0'),
    #         port=port,
    #         threaded=True,
    #         debug=os.environ.get('SERVER_DEBUG', '').lower() == 'true',
    #         )

    # (Send the user to the authorization URL to obtain an authorization code.)


if __name__ == '__main__':
    logger.info('just before run main')
    main()
