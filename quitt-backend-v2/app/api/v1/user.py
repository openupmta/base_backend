from flask import Blueprint
from flask_jwt_extended import jwt_required
from jsonschema import validate
from app.schema.json_schema import schema_user_create
from app.extensions import db, logger
from app.model import Users
import uuid
import datetime

from app.utils import send_result, FieldString, parse_req, send_result, send_error,\
    is_password_contain_space, hash_password

api = Blueprint('users', __name__)


@api.route('', methods=['POST'])
def create_user():
    """ This is api for the user management registers user.

        Request Body:
            username: string, require
                The username of the user. Max length accepted is 50 and minimum length is 1.

            password: string, require
                The password of the user wanted to log in. Max length accepted is 50 and minimum length is 1.

        Returns:

            username: string
                username of newly registered user.

            group_id: string
                group id of this new user.

        Examples::

            curl --location --request POST 'http://<sv_address>:5013/api/v1/users' --header 'Authorization: Bearer <access_token>'
    """

    params = {
        'username': FieldString(requirement=True),
        'password': FieldString(requirement=True),
        'first_name': FieldString(requirement=True),
        'last_name': FieldString(requirement=True),
        'company': FieldString(),
        'address': FieldString(),
        'mobile': FieldString()
    }

    try:
        json_data = parse_req(params)
        # Check valid params
        validate(instance=json_data, schema=schema_user_create)

        username = json_data.get('username', None).lower().strip()
        password = json_data.get('password', None)
        first_name = json_data.get('first_name', None)
        last_name = json_data.get('last_name', None)
        company = json_data.get('company', None)
        address = json_data.get('address', None)
        mobile = json_data.get('mobile', None)
    except Exception as ex:
        logger.error('{} Parameters error: '.format(datetime.datetime.utcnow().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Registers user fail!")

    # log input fields
    # logger.debug(f"INPUT api create user: {json_data}")

    user = Users.find_by_user_name(user_name=username)
    if user:
        return send_error(message="User exist")

    if is_password_contain_space(password):
        return send_error(message='Password cannot contain spaces')

    create_date = datetime.datetime.utcnow().timestamp()
    _id = str(uuid.uuid1())
    user = Users(id=_id, username=username, password_hash=hash_password(password),
                      force_change_password=False, create_date=create_date, modified_date=create_date, is_active=True,
                      firstname=first_name, lastname=last_name, company=company, address=address,
                       mobile=mobile, modified_date_password=create_date)
    user.save_to_db()
    data = {
        'id': _id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'create_date': create_date
    }
    return send_result(data=data, message="Registers user successfully!")
