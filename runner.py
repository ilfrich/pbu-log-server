from typing import Optional
from flask import Flask
from logger import AdvancedLogger
from pbu import Logger
from config import AppConfig
import api.log_api as log_api



if __name__ == '__main__':
    # init config
    config = AppConfig()
    
    # init logger
    logger = AdvancedLogger(config.get_log_folder())

    # create flask app
    app = Flask(__name__)
    log_api.register_endpoints(app, logger, config)


    # start flask app
    app.run(host='0.0.0.0', port=config.get_port(), debug=False)
