import logging
import os
import redis
from flask_jwt_extended import JWTManager
from webargs.flaskparser import FlaskParser
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler

parser = FlaskParser()

os.makedirs("logs", exist_ok=True)
db = SQLAlchemy()
jwt = JWTManager()
# logger
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


logger = setup_logger('api', 'logs/app.log')
logger_auth = setup_logger('auth', 'logs/auth.log')
