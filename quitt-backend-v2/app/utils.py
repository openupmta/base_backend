from time import strftime

from flask import jsonify, request
from app.extensions import parser, logger, logger_auth
from marshmallow import fields, validate as validate_
import joblib
import nltk
from nltk.stem.snowball import GermanStemmer
import re
from app.enums import THRESHOLD
from functools import wraps

# download stopwords
# nltk.download('stopwords')
import json
import werkzeug

# download stopwords
# Load classification model
file_vectorized = 'etc/models/tfidf_vectorizer.sav'
file_model = 'etc/models/logistic_regression.sav'
VECTORIZED = joblib.load(file_vectorized)
LOGISTIC_REGRESSION = joblib.load(file_model)


def parse_req(argmap):
    """
    Parser request from client
    :param argmap:
    :return:
    """
    return parser.parse(argmap)


def send_result(data=None, message="OK", code=200, version=2, status=True):
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
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "version": get_version(version)
    }
    logger.info(res)
    return jsonify(res), 200


def send_error(data=None, message="Error", code=400, version=2, status=False):
    """

    :param data:
    :param message:
    :param code:
    :param version:
    :param status:
    :return:
    """
    res_error = {
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "version": get_version(version)
    }
    logger.error(res_error)
    return jsonify(res_error), code


def get_version(version):
    """
    if version = 1, return api v1
    version = 2, return api v2
    Returns:

    """
    return "v2.0" if version == 2 else "v1.0"


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


def predicting(data):
    """
    :param data: requirements string
    :return:
    """
    # vectorized data
    text_cleaned = clean_text(data)
    data_tranf = VECTORIZED.transform([text_cleaned])
    predict_proba = LOGISTIC_REGRESSION.predict_proba(data_tranf)
    if predict_proba.item(0) >= THRESHOLD:
        return {
            'label': 'Bewirtung',
            'score': predict_proba.item(0)
        }
    elif predict_proba.item(1) >= THRESHOLD:
        return {
            'label': 'Geschenk',
            'score': predict_proba.item(1)
        }
    return {
        'label': "Not in classes"
    }


def clean_text(text):
    """
    :param text:
    :return:
    """
    # stopwords = set(nltk.corpus.stopwords.words('german'))
    file_path = r'etc/models/german.txt'
    with open(file_path) as file:
        file_data = file.read()
    stopwords = file_data.split('\n')
    gs = GermanStemmer()
    text_cleaned = ""
    text_cleaned = re.sub('[^a-zA-Z]', ' ', text)  # Keep only alphabet and space characters
    text_cleaned = text_cleaned.lower()  # All character to lowercase
    text_cleaned = text_cleaned.split()  # Split to list of word (split by space specify character)
    text_cleaned = [gs.stem(word) for word in text_cleaned if not word in stopwords]
    text_cleaned = ' '.join(text_cleaned)
    return text_cleaned


def logger_accountability(func):
    """ Timing and logging all input and output of the function
    :param func: takes any method which elapsed time needs to be calculated
    :return: the result of method with logging the time taken
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        ts = strftime('[%Y-%b-%d %H:%M]')
        result = func(*args, **kwargs)
        logger_auth.info('%s %s %s %s %s %s',
                         ts,
                         request.remote_addr,
                         request.method,
                         request.scheme,
                         request.full_path,
                         result[1])
        logger_auth.info(f"{ts} {func.__name__} output parameters {result[0].json['data']}" )
        # elapsed: float = time() - start
        # pretty = "=" * 50
        # logger.debug(f"{pretty} {func.__name__} {pretty}")
        # logger.info(f"{ts} {func.__name__} took {round(elapsed, 2)}ms")
        # logger.debug(f"{ts} {func.__name__} input parameters {kwargs}")
        # logger.debug(f"{ts} {func.__name__} output parameters {result}")
        # logger.debug("=" * 100)
        return result

    return wrapper

def is_password_contain_space(password):
    """

    Args:
        password:

    Returns:
        True if password contain space
        False if password not contain space

    """
    return ' ' in password


def hash_password(str_pass):
    return werkzeug.security.generate_password_hash(str_pass)

