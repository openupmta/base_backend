from datetime import timedelta
from flask import Blueprint
from app.extensions import jwt, logger, logger_auth
from app.utils import parse_req, FieldString, send_result, send_error, logger_accountability
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, get_jwt_identity,
    create_refresh_token, get_raw_jwt,
)
from app.model import Users, Tokens
from werkzeug.security import check_password_hash
from app.enums import ACCESS_TOKEN, REFRESH_TOKEN

ACCESS_EXPIRES = timedelta(minutes=1)
REFRESH_EXPIRES = timedelta(minutes=5)
api = Blueprint('auth', __name__)


@api.route('/login', methods=['POST'])
@logger_accountability
def login():
    """
    :response: {"messages": "success"}
    """
    params = {
        'username': FieldString(),
        'password': FieldString()
    }
    try:
        json_data = parse_req(params)
        username = json_data.get('username', None).strip()
        password = json_data.get('password')
    except Exception as ex:
        # logger_auth.error(ex.__str__())
        return send_error(message='json_parser_error')
    try:
        # log input fields
        logger_auth.info(f"INPUT api login: {json_data}")

        if len(username) > 50:
            # logger_auth.info("Username can be up to 50 characters")
            return send_error(message="Username can be up to 50 characters")

        if len(password) > 50:
            # logger_auth.info("Password can be up to 50 characters")
            return send_error(message="Password can be up to 50 characters")
        user = Users.query.filter_by(username=username).first()
        if user is None:
            return send_error(message='Invalid username or password. Please try again')

        # Check password
        if not check_password_hash(user.password_hash, password):
            return send_error(message='Invalid username or password. Please try again')

        access_token = create_access_token(identity=user.id, expires_delta=ACCESS_EXPIRES)
        refresh_token = create_refresh_token(identity=user.id, expires_delta=REFRESH_EXPIRES)
        Tokens.save_to_db(access_token)
        Tokens.save_to_db(refresh_token)
        data = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'username': user.username,
            'user_id': user.id
        }
        # logger_auth.info(data)
        return send_result(data=data, message='Logged in successfully!')
    except Exception as ex:
        # logger_auth.error(ex.__str__())
        return send_error(message='login failed')


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@api.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
@logger_accountability
def refresh():
    """
    Refresh token if token is expired
    :return:
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id, expires_delta=ACCESS_EXPIRES)
    refresh_token = create_refresh_token(identity=current_user_id, expires_delta=REFRESH_EXPIRES)
    Tokens.save_to_db(access_token)
    Tokens.save_to_db(refresh_token)
    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': current_user_id
    }
    # logger_auth.info(data)
    return send_result(data=data)


# Endpoint for revoking the current users access token
@api.route('/logout', methods=['DELETE'])
@jwt_required
@logger_accountability
def logout():
    """
    Add token to blacklist
    :return:
    """
    jti = get_raw_jwt()['jti']

    Tokens.revoke_token(jti)
    logger.info("Logout Successfully")
    return send_result(message='Logout Successfully')


# check token revoked_store
@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    return Tokens.is_token_revoked(decrypted_token)
# # Endpoint for revoking the current users refresh token
# @api.route('/logout2', methods=['DELETE'])
# @jwt_refresh_token_required
# def logout2():
#     jti = get_raw_jwt()['jti']
#     # revoked_store.set(jti, 'true', REFRESH_EXPIRES * 1.2)
#     return send_result(message='logout_successfully')
#
#
# # check token revoked_store
# @jwt.token_in_blacklist_loader
# def check_if_token_is_revoked(decrypted_token):
#     jti = decrypted_token['jti']
#     # entry = revoked_store.get(jti)
#     # if entry is None:
#     #     return True
#     return False
