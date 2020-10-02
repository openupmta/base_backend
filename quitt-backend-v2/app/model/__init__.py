# coding: utf-8
from flask_jwt_extended import get_jwt_identity, decode_token

from app.extensions import db
# from bson import ObjectId


class Users(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)
    password_hash = db.Column(db.String)
    force_change_password = db.Column(db.Boolean)
    create_date = db.Column(db.Integer)
    modified_date = db.Column(db.Integer)
    is_active = db.Column(db.Boolean)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    company = db.Column(db.String)
    address = db.Column(db.String)
    mobile = db.Column(db.String)
    modified_date_password = db.Column(db.Integer)

    # def __init__(self, id=None, username=None, password_hash=None, force_change_password=None, create_date=None,
    #              modified_date=None, is_active=None, firstname=None, lastname=None, address=None,
    #              mobile=None, modified_date_password=None):
    #     self.id = id
    #     self.jti = jti
    #     self.token_type = token_type
    #     self.user_identity = user_identity
    #     self.revoked = revoked
    #     self.expires = expires

    def json(self):
        return dict(
            id=self.id,
            username=self.username,
            create_date=self.create_date
        )

    @staticmethod
    def get_all():
        return Users.query.order_by(Users.username).all()

    @staticmethod
    def get_current_user():
        return Users.query.get(get_jwt_identity())

    @staticmethod
    def get_by_id(_id):
        return Users.query.get(_id)

    @classmethod
    def find_by_user_name(cls, user_name):
        return cls.query.filter(cls.username == user_name).first()

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(e.__str__())


class Tokens(db.Model):
    __tablename__ = 'token'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(255))
    token_type = db.Column(db.String)
    user_identity = db.Column(db.String)
    revoked = db.Column(db.Boolean)
    expires = db.Column(db.Integer)

    def __init__(self, jti=None, token_type=None, user_identity=None, revoked=None, expires=None):
        self.id = None
        self.jti = jti
        self.token_type = token_type
        self.user_identity = user_identity
        self.revoked = revoked
        self.expires = expires

    def json(self):
        return dict(
            id=self.id,
            jti=self.jti,
            token_type=self.token_type,
            user_identity=self.user_identity,
            revoked=self.revoked,
            expires=self.expires
        )

    @classmethod
    def parse_to_object(self, encoded_token=None):
        data = Tokens()
        decoded_token = decode_token(encoded_token)
        data.jti = decoded_token['jti']
        data.user_identity = decoded_token['identity']
        data.token_type = decoded_token['type']
        data.expires = decoded_token['exp']
        data.revoked = 0
        return data

    @classmethod
    def save_to_db(self, encoded_token=None):
        try:
            token = self.parse_to_object(encoded_token=encoded_token)
            db.session.add(token)
            db.session.commit()
        except Exception as e:
            print(e.__str__())

    @classmethod
    def revoke_token(self,jti):
        """
        Revokes the given token. Raises a TokenNotFound error if the token does
        not exist in the database
        """
        try:
            token = Tokens.query.filter_by(jti=jti).first()
            token.revoked = True
            db.session.commit()
        except Exception as e:
            print(e.__str__())

    @staticmethod
    def is_token_revoked(decoded_token):
        """
        Checks if the given token is revoked or not. Because we are adding all the
        tokens that we create into this database, if the token is not present
        in the database we are going to consider it revoked, as we don't know where
        it was created.
        """
        jti = decoded_token['jti']
        try:
            token = Tokens.query.filter_by(jti=jti).one()
            return token.revoked
        except Exception:
            return True


class PredictHistory(db.Model):
    __tablename__ = 'predict_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data = db.Column(db.String)
    label = db.Column(db.String)
    score = db.Column(db.Float)
    description = db.Column(db.String)

    def __init__(self, data=None, label=None, score=None, description=None):
        self.id = None
        self.data = data
        self.label = label
        self.score = score
        self.description = description

    def json(self):
        return dict(
            id=self.id,
            data=self.data,
            label=self.label,
            score=self.score,
            description=self.description
        )

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(e.__str__())