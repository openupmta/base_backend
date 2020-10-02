# -*- coding: utf-8 -*-
import traceback
from time import strftime
from flask import Flask, request, jsonify
from app.extensions import jwt
from app.api import v1 as api_v1
from app.extensions import logger, parser, db, logger_auth
from .settings import ProdConfig
from .utils import send_error


def create_app(config_object=ProdConfig):
    """Init App Register Application extensions and API prefix

    Args:
        config_object: We will use Prod Config when the environment variable has FLASK_DEBUG=1.
        You can run export FLASK_DEBUG=1 in order to run in application dev mode.
        You can see config_object in the settings.py file
    """
    app = Flask(__name__, static_url_path="", static_folder="./files", template_folder="./template")
    app.config.from_object(config_object)
    register_extensions(app, config_object)

    register_blueprints(app)
    return app


def register_extensions(app, config_object):
    """Init extension. You can see list extension in the extensions.py

    Args:
        app: Flask handler application
        config_object: settings of the application
    """
    # Order matters: Initialize SQLAlchemy before Marshmallow
    # create log folder
    db.app = app
    jwt.init_app(app)
    db.init_app(app)

    @app.after_request
    def after_request(response):
        # This IF avoids the duplication of registry in the log,
        # since that 500 is already logged via @app.errorhandler.
        if response.status_code != 500:
            ts = strftime('[%Y-%b-%d %H:%M]')
            logger.info('%s %s %s %s %s %s',
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
        error = '{} {} {} {} {} {} 5xx INTERNAL SERVER ERROR\n{}'.format(
            ts,
            request.remote_addr,
            request.method,
            request.scheme,
            request.full_path,
            tb,
            str(e)
        )

        logger.error(error)
        logger_auth.error(error)
        return send_error(message='INTERNAL SERVER ERROR', code=500)

    @parser.error_handler
    def handle_error(error, req, schema, *, error_status_code, error_headers):
        return send_error(message='Parser error. Please check your requests body', code=error_status_code)

    # Return validation errors as JSON
    @app.errorhandler(422)
    @app.errorhandler(400)
    def handle_error(err):
        headers = err.data.get("headers", None)
        messages = err.data.get("messages", ["Invalid request."])
        if headers:
            return jsonify({"errors": messages}), err.code, headers
        else:
            return jsonify({"errors": messages}), err.code


def register_blueprints(app):
    """Init blueprint for api url
    :param app: Flask application
    """
    app.register_blueprint(api_v1.predict.api, url_prefix='/api/v1/predict')
    app.register_blueprint(api_v1.auth.api, url_prefix='/api/v1/auth')
    app.register_blueprint(api_v1.user.api, url_prefix='/api/v1/users')
