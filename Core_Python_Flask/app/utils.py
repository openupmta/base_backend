from flask import jsonify
from werkzeug.security import safe_str_cmp
from .extensions import parser, client
import datetime
import werkzeug
import re
import string, random
from marshmallow import fields, validate as validate_

patterns = [r'§[ ]*[\d]+[ ]*[der |des |von der |vom ]*[{}]+',
            r'§[ ]*[\d]+[ ]*[Abs.|Absatz]+[ ]*[\d]+[ ]*[der |des |von der |vom ]*[{}]+',
            r'§[ ]*[\d]+[ ]*[Abs.|Absatz]+[ ]*[\d]+[ ]*[Nr.|Nummer|Satz]+[ ]*[\d]+[ ]*[der |des |von der |vom ]*[%s]+']


def parse_req(argmap):
    """
    Parser request from client
    :param argmap:
    :return:
    """
    return parser.parse(argmap)


def send_result(data=None, message="OK", code=200, version=1, status=True):
    """
    Args:
        data: simple result object like dict, string or list
        message: message send to client, default = OK
        code: code default = 200
        version: version of api
    :param data:
    :param message:
    :param code:
    :param version:
    :param status:
    :return:
    json rendered sting result
    """
    res = {
        "jsonrpc": "2.0",
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "version": get_version(version)
    }

    return jsonify(res), 200


def send_error(data=None, message="Error", code=200, version=1, status=False):
    """

    :param data:
    :param message:
    :param code:
    :param version:
    :param status:
    :return:
    """
    res_error = {
        "jsonrpc": "2.0",
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "version": get_version(version)
    }
    return jsonify(res_error), code


def get_version(version):
    """
    if version = 1, return api v1
    version = 2, return api v2
    Returns:

    """
    return "ERP v2.0" if version == 2 else "ERP v1.0"


class FieldString(fields.String):
    """
    validate string field, max length = 1024
    Args:
        des:

    Returns:

    """
    DEFAULT_MAX_LENGTH = 1024  # 1 kB

    def __init__(self, validate=None, requirement=None, **metadata):
        """

        Args:
            validate:
            metadata:
        """
        if validate is None:
            validate = validate_.Length(max=self.DEFAULT_MAX_LENGTH)
        if requirement is not None:
            validate = validate_.NoneOf(error='Dau vao khong hop le!', iterable={'full_name'})
        super(FieldString, self).__init__(validate=validate, required=requirement, **metadata)


class FieldNumber(fields.Number):
    """
    validate number field, max length = 30
    Args:
        des:

    Returns:

    """
    DEFAULT_MAX_LENGTH = 30  # 1 kB

    def __init__(self, validate=None, **metadata):
        """

        Args:
            validate:
            metadata:
        """
        if validate is None:
            validate = validate_.Length(max=self.DEFAULT_MAX_LENGTH)
        super(FieldNumber, self).__init__(validate=validate, **metadata)


def check_datetime(str_data):
    if str_data is None:
        return send_error(message='Date is None')
    return str_data.strip().isdigit()


def check_email(str_email):
    return re.match(
        r"^[A-Za-z0-9]*[A-Za-z]+[A-Za-z0-9]*(\.)[A-Za-z]+(@)(BOOT|BOOt|BOot|Boot|boot|booT|boOT|bOOT|bOOt|bOot|boOt|bOoT|BoOT|BOoT|BooT|BoOt)(\.)(ai|AI|Ai|aI)$",
        str_email)


def check_email_contact(str_email):
    return re.match(r"^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$", str_email)


def get_datetime_now():
    return datetime.datetime.now()


def get_datetime_now_h():
    return datetime.datetime.now().strftime('%Hh%M\'')


def get_month_now():
    return datetime.datetime.now().month





def hash_password(str_pass):
    return werkzeug.security.generate_password_hash(str_pass)




def check_password(str_pass):
    a = re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,50}$", str_pass)
    return a


def check_full_name(str_data):
    result = re.match(r"^[^\d\s~!@#$%^&*()_+=]*\s*[^\d~!@#$%^&*()_+=]*[^\d\s~!@#$%^&*()_+=]+$", str_data)
    return result


def check_phone_number(str_data):
    result = re.match(r"^[\d\s()+-]{7,20}$", str_data)
    return result


def set_auto_MaNV():
    lst = []
    list_user = client.db.user.find({}, {'MaNV': 1})
    if list_user is None:
        return 'BA001'
    list_user = list(list_user)
    for i in list_user:
        lst.append(i['MaNV'])
    tmp = max(lst)
    str1 = tmp[0:2]
    stt = int(tmp[2: len(tmp)]) + 1
    mnv = str1 + '{:03d}'.format(stt)
    return mnv


def random_pwd():
    symbol_list = ["@", "$", "!", "%", "*", "?", "&"]
    pw_list = ([random.choice(symbol_list),
                random.choice(string.digits),
                random.choice(string.ascii_lowercase),
                random.choice(string.ascii_uppercase)
                ]
               + [random.choice(string.digits) for i in range(4)])
    random.shuffle(pw_list)
    pw = ''.join(pw_list)
    return pw


