from marshmallow import fields
from flask import Blueprint, request
from app.enums import USER_ACTIVATED, USER_DEACTIVATED, STATUS_USER
from app.utils import parse_req, FieldString, send_result, send_error, hash_password, set_auto_MaNV
from app.extensions import client
from bson import ObjectId
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    get_jwt_claims
)

api = Blueprint('user', __name__)

"""
Function: User registration - Admin right required
Input: user_name, password, email, fullname, group_role_id
Output: Success / Error Message
"""
@api.route('/create', methods=['POST'])
@jwt_required
def post():

    params = {
        'user_name': FieldString(requirement=True),
        'password': FieldString(requirement=True),
        'email': FieldString(requirement=True),
        'full_name': FieldString(requirement=True),
        'group_role_id': fields.Number()
    }

    try:
        json_data = parse_req(params)
        full_name = json_data.get('full_name', None)
        email = json_data.get('email', None).lower()
        user_name = json_data.get('user_name', None)
        password = json_data.get('password', None)
        group_role_id = json_data.get('group_role_id', 0)


    except Exception:
        return send_error(message='Lỗi dữ liệu đầu vào')

    '''check conditions'''

    '''end check'''

    '''create MNV auto'''

    '''end create MNv'''
    _id = str(ObjectId())
    user = {
        '_id': _id,
        'full_name': full_name,
        'user_name': user_name,
        'password': hash_password(password),
        'email': email,
        'group_role_id': int(group_role_id),
        'status': USER_ACTIVATED,
        'MaNV': set_auto_MaNV()
    }
    try:
        client.db.user.insert_one(user)
    except Exception:
        return send_error(message='có lỗi ngoại lệ sảy ra')

    return send_result(message="Tạo user thành công ", data=user)


"""
Function: Update user's profile - Admin right required
Input: user_id
Output: Success / Error Message
"""


@api.route('/update', methods=['PUT'])
@jwt_required
def put():
    claims = get_jwt_claims()
    if not claims['is_admin']:
        return send_error(message="Bạn không đủ quyền để thực hiện thao tác này")

    user_id = request.args.get('user_id')
    user = client.db.user.find_one({'_id': user_id})
    if user is None:
        return send_error(message='Không tìm thấy người dùng.')

    params = {
        'user_name': FieldString(requirement=True),
        'password': FieldString(requirement=True),
        'email': FieldString(requirement=True),
        'full_name': FieldString(requirement=True),
        'group_role_id': fields.Number(),
        'status': fields.Number()
    }

    try:
        json_data = parse_req(params)
        full_name = json_data.get('full_name', None)
        email = json_data.get('email', None).lower()
        user_name = json_data.get('user_name', None)
        password = json_data.get('password', None)
        group_role_id = json_data.get('group_role_id', 0)
        status = json_data.get('status', 0)


    except Exception:
        return send_error(message='Lỗi dữ liệu đầu vào')
    '''Check '''
    if status == USER_ACTIVATED:
        status = USER_ACTIVATED
    elif status == USER_DEACTIVATED:
        status = USER_DEACTIVATED
    else:
        return send_error(message="Bạn chưa nhập trạng thái")
    '''End check'''
    _id = str(ObjectId())
    new_user = {
        '$set': {
            'full_name': full_name,
            'user_name': user_name,
            'password': hash_password(password),
            'email': email,
            'group_role_id': int(group_role_id),
            'status': int(status),
        }}
    try:
        client.db.user.update_one({'_id': user_id}, new_user)
    except Exception:
        return send_error(message='có lỗi ngoại lệ sảy ra')
    return send_result(message="Cập nhật thành công", data=user)


"""
Function: Update user's profile - Admin right required
Input: user_id
Output: Success / Error Message
"""


@api.route('/delete', methods=['DELETE'])
@jwt_required
def delete():
    user_id = request.args.get('user_id')
    user = client.db.user.find_one({'_id': user_id})
    if user is None:
        return send_error(message="Không tìm thấy dự liệu đầu vào trong cơ sở dữ liệu")
    try:
        client.db.user.delete_one({'_id': user_id})
    except Exception:
        return send_error(message="Lỗi xóa không thành công")

    return send_result(message="Xóa thành công")


"""
Function: Get all page
Input: 
Output: Success / Error Message
"""


@api.route('/get_all_page_search', methods=['GET'])
@jwt_required
def get_all_page_search():
    text_search = request.args.get('text_search', '')
    page_size = request.args.get('page_size', '25')
    page_number = request.args.get('page_number', '0')
    skips = int(page_size) * int(page_number)
    '''Give list after filtering'''
    query = \
        {'$and': [
            {'status': USER_ACTIVATED},
            {'$or': [
                {'email': {'$regex': text_search, '$options': "$i"}},
                {'MaNV': {'$regex': text_search, '$options': "$i"}},
                {'full_name': {'$regex': text_search, '$options': "$i"}}
            ]}
        ]}
    users = client.db.user.find(query).skip(skips).limit(int(page_size))
    '''end list'''
    list_user = list(users)
    '''Make a request'''

    for i in list_user:
        if int(i['status']) == USER_ACTIVATED:
            i['status_name'] = STATUS_USER[USER_ACTIVATED]
        if int(i['status']) == USER_DEACTIVATED:
            i['status_name'] = STATUS_USER[USER_DEACTIVATED]
    '''end request'''
    totals = client.db.user.find().count()
    data = {
        'totals': totals,
        'results': list_user
    }
    return send_result(data=data)
"""
Function: Get all page
Input: 
Output: Success / Error Message
"""


@api.route('/get_all_page', methods=['GET'])
@jwt_required
def get_all_page():
    page_size = request.args.get('page_size', '25')
    page_number = request.args.get('page_number', '0')
    skips = int(page_size) * int(page_number)
    users = client.db.user.find().skip(skips).limit(int(page_size))
    list_user = list(users)
    '''Make a request'''

    for i in list_user:
        if int(i['status']) == USER_ACTIVATED:
            i['status_name'] = STATUS_USER[USER_ACTIVATED]
        if int(i['status']) == USER_DEACTIVATED:
            i['status_name'] = STATUS_USER[USER_DEACTIVATED]
    '''end request'''
    totals = client.db.user.find().count()
    data = {
        'totals': totals,
        'results': list_user
    }
    return send_result(data=data)
