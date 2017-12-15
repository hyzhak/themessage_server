import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

from flask import Flask, jsonify
import medium
import os
from themessage_server import medium_controller

app = Flask(__name__)
app.register_blueprint(medium_controller.medium_blueprint, url_prefix='/medium')


@app.route('/')
def root_router():
    return jsonify({'status': 'ok'})


def main():
    port_string = os.environ.get('SERVER_PORT', None)
    port = int(port_string) if port_string else None

    app.run(host=os.environ.get('SERVER_IP', '0.0.0.0'),
            port=port,
            debug=os.environ.get('SERVER_DEBUG', '').lower() == 'true',
            )

    # (Send the user to the authorization URL to obtain an authorization code.)


if __name__ == '__main__':
    logger.info('just before run main')
    main()
