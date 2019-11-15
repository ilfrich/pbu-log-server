from flask import Flask, request, abort, jsonify
from pbu import Logger, JSON
from config import get_log_folder, get_port, get_auth_token, get_enabled_log_levels
from logging import LogRecord


def extract_auth_token():
    key = "Authorization"
    if key in request.headers:
        return request.headers[key]
    return None


if __name__ == '__main__':
    # initialise logger
    logger = Logger("MAIN", log_folder=get_log_folder(), enable_logger_name=False,
                    enabled_log_levels=get_enabled_log_levels())
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
            logger.warn("Incoming request with invalid authentication")
            abort(401)

        message = JSON(request.get_json())
        lr = LogRecord(message.name, message.levelno, message.pathname, message.lineno,
                       message.msg, message.args, None)
        logger.handle(lr)
        return jsonify({"status": True})


    # start flask app
    app.run(host='0.0.0.0', port=get_port(), debug=False)
