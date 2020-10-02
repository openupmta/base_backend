# -*- coding: utf-8 -*-
import logging
import traceback
from time import strftime
from flask import Flask, request
from flask import request
from app.api import v1 as api_v1
from app.extensions import jwt, client, app_log_handler, socketio
from .settings import ProdConfig


users={}


def create_app(config_object=ProdConfig, content='app'):
    """
    Init App
    :param config_object:
    :param content:
    :return:
    """
    app = Flask(__name__, static_url_path="", static_folder="./template", template_folder="./template")
    app.config.from_object(config_object)
    register_extensions(app, content, config_object)
    register_blueprints(app)
    return app


def register_extensions(app, content, config_object):
    """
    Init extension
    :param app:
    :param content:
    :return:
    """
    client.app = app
    client.init_app(app)
    socketio.init_app(app)
    # don't start extensions if content != app
    if content == 'app':
        jwt.init_app(app)
    # logger
    logger = logging.getLogger('api')
    logger.setLevel(logging.ERROR)
    logger.addHandler(app_log_handler)

    @app.after_request
    def after_request(response):
        # This IF avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if response.status_code != 500:
            ts = strftime('[%Y-%b-%d %H:%M]')
            logger.error('%s %s %s %s %s %s',
                         ts,
                         request.remote_addr,
                         request.method,
                         request.scheme,
                         request.full_path,
                         response.status)
        return response

    @app.errorhandler(Exception)
    def exceptions(e):
        ts = strftime('[%Y-%b-%d %H:%M]')
        tb = traceback.format_exc()
        error = '{} {} {} {} {} 5xx INTERNAL SERVER ERROR\n{}'.format \
                (
                ts,
                request.remote_addr,
                request.method,
                request.scheme,
                request.full_path,
                tb
            )

        logger.error(error)

        return "Internal Server Error", 500


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = client.db.user.find_one({'_id': identity})
    if user['group_role_id'] == '1':
        return {'is_admin': True, 'is_user': False}
    else:
        return {'is_admin': False, 'is_user': False}


def register_blueprints(app):
    """
    Init blueprint for api url
    :param app:
    :return:
    """
    app.register_blueprint(api_v1.auth.api, url_prefix='/api/v1/auth')
    app.register_blueprint(api_v1.user.api, url_prefix='/api/v1/user')

