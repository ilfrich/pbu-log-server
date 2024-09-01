import warnings
from datetime import datetime, timedelta
from pytz import timezone
from logging import LogRecord
from flask import request, abort, jsonify, Flask, render_template
from config import AppConfig
from logger import AdvancedLogger, LOG_STR
from pbu import JSON, DATE_FORMAT, set_timezone


def extract_auth_token():
    key = "Authorization"
    if key in request.headers:
        return request.headers[key]
    return None


def register_endpoints(app: Flask, logger: AdvancedLogger, config: AppConfig):

    auth_token = config.get_auth_token()

    def auth_check():
        if auth_token is not None and auth_token != extract_auth_token():
            warnings.warn("Incoming request with invalid authentication")
            abort(401)

    @app.route("/", methods=["GET"])
    def get_frontend():
        return render_template("index.html")

    if config.is_debug():
        @app.after_request
        def add_header(r):
            """
            Add headers to both force latest IE rendering engine or Chrome Frame,
            and also to cache the rendered page for 10 minutes.
            """
            r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            r.headers["Pragma"] = "no-cache"
            r.headers["Expires"] = "0"
            r.headers['Cache-Control'] = 'public, max-age=0'
            return r


     # declare API handler for incoming log messages
    @app.route("/api/log", methods=["POST"])
    def log_message():
        auth_check()
        message = JSON(request.get_json())
        msg = message.msg
        if "trace" in message and message.trace is not None and isinstance(message.trace, list):
            trace = "\n".join(message.trace)
            msg = f"{msg}\n{trace}"

        lr = LogRecord(message.name, message.levelno, message.pathname, message.lineno,
                       msg, message.args, None)
        logger.log_message(lr)
        return jsonify({"status": True})

    @app.route("/api/login-check", methods=["GET"])
    def get_login_check():
        auth_check()        
        log_levels = [LOG_STR[code] for code in config.get_enabled_log_levels()]
        return jsonify({"logLevels": log_levels})

    @app.route("/api/log/messages", methods=["GET"])
    def get_log_messages():
        auth_check()
        tz_name = request.args.get("timezone", "UTC")
        date = request.args.get("date", None)
        level = request.args.get("level", None)
        if date is None or level is None:
            abort(400)

        start_date = set_timezone(datetime.strptime(date, DATE_FORMAT), timezone(tz_name))
        end_date = start_date + timedelta(days=1)

        messages = logger.get_log_messages(level, start_date, end_date)
        return jsonify(messages)
