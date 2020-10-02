from bson import ObjectId
from datetime import timedelta
from flask import Blueprint
from app.extensions import jwt, client, red
from app.utils import parse_req, FieldString, send_result, send_error
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, get_jwt_identity,
    create_refresh_token, get_raw_jwt, get_jti
)
ACCESS_EXPIRES = timedelta(days=30)
REFRESH_EXPIRES = timedelta(days=30)
revoked_store = red
api = Blueprint('auth', __name__)


@api.route('/login', methods=['POST'])
def login():
    """
    :response: {"messages": "success"}
    """
    params = {
        'email': FieldString(),
        'password': FieldString()
    }

    try:
        json_data = parse_req(params)
        email = json_data.get('email', None).lower()
        password = json_data.get('password')
    except Exception as ex:
        return send_error(message='json_parser_error')

    user = client.db.user.find_one({'email': email})
    if user is None:
        return send_error(message='Email không tồn tại')

    # if not check_password_hash(user['password'], password):
    #     return send_error(message='Bạn đã nhập sai mật khẩu vui lòng nhập lại')

    access_token = create_access_token(identity=user['_id'], expires_delta=ACCESS_EXPIRES)
    refresh_token = create_refresh_token(identity=user['_id'], expires_delta=REFRESH_EXPIRES)
    access_jti = get_jti(encoded_token=access_token)
    refresh_jti = get_jti(encoded_token=refresh_token)
    revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
    revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)
    user_token = dict(
        _id=str(ObjectId()),
        user_id=user['_id'],
        access_jti=access_jti,
        refresh_jti=refresh_jti
    )
    client.db.token.insert_one(user_token)
    return send_result(data={'access_token': access_token, 'refresh_token': refresh_token,
                             'email': user['email'], 'full_name': user['full_name'],
                             }, message='Đăng nhập thành công')


# The jwt_refresh_token_required decorator insures a valid refresh
# token is present in the request before calling this endpoint. We
# can use the get_jwt_identity() function to get the identity of
# the refresh token, and use the create_access_token() function again
# to make a new access token for this identity.
@api.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """
    Refresh token if token is expired
    :return:
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    access_jti = get_jti(encoded_token=access_token)
    revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
    refresh_jti = get_raw_jwt()['jti']
    user_token = dict(
        _id=str(ObjectId()),
        user_id=current_user_id,
        access_jti=access_jti,
        refresh_jti=refresh_jti
    )
    client.db.token.insert_one(user_token)

    ret = {
        'access_token': access_token
    }
    return send_result(data=ret)


# Endpoint for revoking the current users access token
@api.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """
    Add token to blacklist
    :return:
    """
    jti = get_raw_jwt()['jti']
    revoked_store.set(jti, 'true', ACCESS_EXPIRES * 1.2)

    # remove token from database
    client.db.token.remove({'access_jti': jti})

    return send_result(message='logout_successfully')


# Endpoint for revoking the current users refresh token
@api.route('/logout2', methods=['DELETE'])
@jwt_refresh_token_required
def logout2():
    jti = get_raw_jwt()['jti']
    revoked_store.set(jti, 'true', REFRESH_EXPIRES * 1.2)
    return send_result(message='logout_successfully')


# check token revoked_store
@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    jti = decrypted_token['jti']
    entry = revoked_store.get(jti)
    if entry is None:
        return True
    return False
