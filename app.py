from flask import Flask, jsonify
from flask_restful import Api
from datetime import timedelta
from flask_jwt_extended import JWTManager

from db import db
from blacklist import BLACKLIST
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.user import UserRegister
from resources.commercial import Commercial, CommercialList
from resources.vente import Vente, VenteList, VenteStat
from resources.produit import Produit, ProduitList
from resources.client import Client, ClientList

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root''@localhost/data_db'

JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=1)
# JWT_TOKEN_LOCATION = 'cookies'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.secret_key = 'diallo'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST
    
@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401

api.add_resource(CommercialList, '/commerciaux')
api.add_resource(Commercial, '/commerciaux', '/commerciaux/<int:id>', endpoint='commerciaux')
api.add_resource(ProduitList, '/produits')
api.add_resource(Produit, '/produits', '/produits/<int:id>', endpoint='produits')
api.add_resource(ClientList, '/clients')
api.add_resource(Client, '/clients', '/clients/<int:id>', endpoint="clients")
api.add_resource(VenteList, '/ventes')

api.add_resource(VenteStat, '/vente_interval/<string:date_debut>/<string:date_fin>')

api.add_resource(Vente, '/ventes', '/ventes/<int:id>', endpoint="ventes")
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/users/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
    