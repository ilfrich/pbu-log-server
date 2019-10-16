from flask import Flask, request, abort, jsonify
from pbu import Logger, JSON
from config import get_log_folder, get_port, get_auth_token


def extract_auth_token():
    key = "Authorization"
    if key in request.headers:
        return request.headers[key]
    return None


if __name__ == '__main__':
    # initialise logger
    logger = Logger("MAIN", log_folder=get_log_folder())
    logger.info("==========================================")
    logger.info("           Starting Log Server")
    logger.info("==========================================")

    # create flask app
    app = Flask(__name__)

    # load from config, if required
    auth_token = get_auth_token()

    # declare API handler for incoming log messages
    @app.route("/api/log", methods=["POST"])
    def log_message():
        if auth_token is not None and auth_token != extract_auth_token():
            abort(401)

        def _format_message(msg):
            return "[{}] {}".format(msg.name, msg.msg)

        message = JSON(request.get_json())
        if message.levelname == "INFO":
            logger.info(_format_message(message))
        elif message.levelname == "ERROR":
            logger.error(_format_message(message))
        elif message.levelname == "WARN":
            logger.warn(_format_message(message))
        elif message.levelname == "DEBUG":
            logger.debug(_format_message(message))

        return jsonify({"status": True})

    # start flask app
    app.run(host='0.0.0.0', port=get_port())
