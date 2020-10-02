from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.utils import parse_req, FieldString, send_result, send_error, predicting
from app.model import PredictHistory

api = Blueprint('predict', __name__)


@api.route('', methods=['POST'])
@jwt_required
def predict():
    """predict text
    :return:
    """
    params = {
        'data': FieldString()
    }
    try:
        json_data = parse_req(params)
        data = json_data.get('data', None).lower()
    except Exception as ex:
        return send_error(message='json_parser_error')
    result = predicting(data)
    history = PredictHistory(data=data, label=None if 'score' not in result.keys() else result["label"],
                             score=None if 'score' not in result.keys() else result["score"],
                             description="Not in classes!" if 'score' not in result.keys() else "Predict successfully!")
    history.save_to_db()
    # db.session.commit()
    return send_result(data=result)