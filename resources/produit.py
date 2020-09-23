from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity, jwt_optional, fresh_jwt_required
from models.produit import ProduitModel

import datetime

class Produit(Resource):
	parser = reqparse.RequestParser()

	parser.add_argument('product_name',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('desc',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('date_mise_vente',
						type=lambda x: datetime.datetime.strptime(x,"%Y-%m-%d"),
						nullable=False,
						required=True,
						)
	

	parser.add_argument('status',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('type_produit',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('code',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('prix_produit',
						type=float,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('user_id',
						type=int,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	@jwt_required
	def get(self, id):
		produit = ProduitModel.find_by_id(id)
		current_user_id = get_jwt_identity()
		if current_user_id:
			if produit and produit.user_id == current_user_id:
				return produit.json()

			return {'message': 'Product not found'}, 404
		return {"message": "Veuille vous conneter"}		
	@jwt_required	
	def post(self):

		data = Produit.parser.parse_args()

		if ProduitModel.find_by_code(data['code']):
			return {'message': "A Product with that code already exists."}, 400

		product_name = data['product_name']
		if not product_name:
			return {'message': "Veuilez entrer le nom du produit"}

		desc = data['desc']
		if not desc:
			return {'message': "Veuilez entrer la description du produit"}

		date_mise_vente = data['date_mise_vente']
		if not date_mise_vente:
			return {'message': "Veuilez entrer la date de mise en vente du produit"}

		status = data['status']
		if not status:
			return {'message': "Veuilez entrer le status du prduit"}

		type_produit = data['type_produit']
		if not type_produit:
			return {'message': "Veuilez entrer le type du prduit"}

		code = data['code']
		if not code:
			return {'message': "Veuilez entrer le code du prduit"}	

		prix_produit = data['prix_produit']
		if not prix_produit:
			return {'message': "Veuiller entrer le produit"}


		produit = ProduitModel(**data)

		try:
			produit.save_to_db()
		except:
			return {"message": "An error occurred creating the commercial."}, 500

		return produit.json(), 201	 

	@jwt_required
	def delete(self, id):
		current_user_id = get_jwt_identity()
		produit = ProduitModel.find_by_id(id)
		if current_user_id:
			if produit and current_user_id == produit.user_id:
				produit.delete_from_db()
				return {'message': 'Product deleted'}

			return {'message': 'Product not found.'}, 404
		return {"message": "Veuillez-vous connecter"}	

	@jwt_required
	def put(self, id):
		current_user_id = get_jwt_identity()
		if current_user_id:

			data = Produit.parser.parse_args()

			produit = ProduitModel.find_by_id(id)
			if produit and produit.user_id == current_user_id:
				product_name = data['product_name']
				if not product_name:
					return {'message': "Veuilez entrer le nom du produit"}

				desc = data['desc']
				if not desc:
					return {'message': "Veuilez entrer la description du produit"}

				date_mise_vente = data['date_mise_vente']
				if not date_mise_vente:
					return {'message': "Veuilez entrer la date de mise en vente du produit"}

				status = data['status']
				if not status:
					return {'message': "Veuilez entrer le status du produit"}

				type_produit = data['type_produit']
				if not type_produit:
					return {'message': "Veuilez entrer le type du produit"}

				code = data['code']
				if not code:
					return {"message": "Le code ne dois pas etre un champs vide"}

				prix_produit = data['prix_produit']
				if not prix_produit:
					return {'message': "Veuiller entrer le produit"}	

				if ProduitModel.find_by_code(code):
					return {"message": "Un produit avec ce code existe deja"}	


				produit.product_name = product_name
				produit.desc = desc
				produit.date_mise_vente = date_mise_vente
				produit.status = status
				produit.type_produit = type_produit
				produit.prix_produit = prix_produit
				produit.code = code

				produit.save_to_db()
				return produit.json()
			return {'message': 'Product not found.'}, 404

		return {"Veuillez-vous connecter."}
class ProduitList(Resource):
	@jwt_optional
	def get(self):
		user_id = get_jwt_identity()
		if not user_id:
			return {"message": "connectez-vous pour avoir plus d'information"}
			
		produits = [x.json() for x in ProduitModel.query.filter(ProduitModel.user_id==user_id).all()]	
		return {"nombre_de_produit": len(produits),
				"produit": produits
			}

		
		