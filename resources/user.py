from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
import re
from models.user import UserModel
from blacklist import BLACKLIST

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                    type=str,
                    required=True,
                    nullable=False,
                    help="This field cannot be blank."
                    )

_user_parser.add_argument('email',
                    type=str,
                    required=True,
                    nullable=False,
                    help="This field cannot be blank."
                    )

_user_parser.add_argument('password',
                    type=str,
                    required=True,
                    nullable=False,
                    help="This field cannot be blank."
                    )

class UserRegister(Resource):


    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists"}, 400

        if UserModel.find_by_email(data['email']):
            return {"message": "A user with that email already exists"}, 400

        username = data['username']
        if not username:
            return {"message": "Veuillez entrer le username"}

        email = data['email']
        if not email:
            return {"message": "Veuillez entrer votre mail"}

        match = re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)
        if not match:
            return {"message": "Movaise adresse mail"}    
            
        password = data['password']
        if not password:
            return {"message": "Veuillez entrer un mot de passe"}
        if len(password) < 8:
            return {"message": "Mot de passe trop court vous devez entrez au moyen 8 caractéres"}
                    
        user = UserModel(data['username'], data['email'], data['password'])
        user.save_to_db()

        return {"message": "User created successfully."}, 201

class User(Resource):
    
    @jwt_required
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        return user.json(), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username',
                type=str,
                required=True,
                nullable=False,
                help="This field cannot be blank."
                )

    parser.add_argument('password',
                type=str,
                required=True,
                nullable=False,
                help="This field cannot be blank."
                )
    def post(self):
        data = UserLogin.parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if user and safe_str_cmp(user.password, data['password']):

            access_token = create_access_token(identity=user.id, fresh=True) 
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {"message": "Invalid Credentials!"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']  # jti is "JWT ID", a unique identifier for a JWT.
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200      


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):

        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
        