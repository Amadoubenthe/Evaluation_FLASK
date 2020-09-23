from flask_restful import Resource, reqparse
from sqlalchemy import func
import inspect
from sqlalchemy.sql import func
from db import db
from sqlalchemy import desc
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity, jwt_optional, fresh_jwt_required
from models.vente import VenteModel
from models.commercial import CommercialModel
from models.produit import ProduitModel
import datetime

class Vente(Resource):
	parser = reqparse.RequestParser()

	parser.add_argument('produit_id',
						type=int,
						required=True,
						nullable=False,
						help="Every vente needs a produit_id.!"
						)

	parser.add_argument('commercial_id',
						type=int,
						required=True,
						nullable=False,
						help="Every vente needs a commercial_id.!"
						)

	parser.add_argument('client_id',
						type=int,
						required=True,
						nullable=False,
						help="Every vente needs a client_id.!"
						)

	parser.add_argument('date_de_vente',
						type=lambda x: datetime.datetime.strptime(x,"%Y-%m-%d"),
						nullable=False,
						required=True,
						)

	parser.add_argument('user_id',
						type=int,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	@jwt_required
	def get(self, id):
		current_user_id = get_jwt_identity()
		if current_user_id:
			vente = VenteModel.find_by_id(id)
			if vente and vente.user_id == current_user_id:
				return vente.json()

			return {'message': 'Vente not found'}, 404
		return {"message": "Veuillez-vous connectez"}

	def post(self):
		data = Vente.parser.parse_args()

		date_de_vente = data['date_de_vente']
		if not date_de_vente:
			return {'message': "Veuillez entrer la date de vente"}

		produit_id = data['produit_id']
		if not produit_id:
			return {'message': "Veuillez entrer l'id du produit"}

		commercial_id = data['commercial_id']
		if not commercial_id:
			return {'message': "Veuillez entrer l'id du commercial."}

		client_id = data['client_id']
		if not client_id:
			return {'message': "Veuillez entrer l'id du client."}	

		vente = VenteModel(**data)

		try:
			vente.save_to_db()

		except:
			return {"message": "An error occurred creating the vente."}, 500

		return vente.json(), 201

	@jwt_required
	def delete(self, id):
		current_user_id = get_jwt_identity()
		vente = VenteModel.find_by_id(id)

		if vente and vente.user_id == current_user_id:
			vente.delete_from_db()
			return {'message': 'vente deleted'}

		return {'message': 'vente not found'}	

	@jwt_required	
	def put(self, id):
		current_user_id = get_jwt_identity()
		data = Vente.parser.parse_args()
		vente = VenteModel.find_by_id(id)
		if vente and vente.user_id == current_user_id:
			date_de_vente = data['date_de_vente']
			if not date_de_vente:
				return {'message': "Veuilez entrer la date vente du produit"}
			produit_id = data['produit_id']
			if not produit_id:
				return {'message': "Veuillez entrer l'id du produit"}

			commercial_id = data['commercial_id']
			if not commercial_id:
				return {'message': "Veuillez entrer l'id du commercial."}

			client_id = data['client_id']
			if not client_id:
				return {'message': "Veuillez entrer l'id du client."}

			vente.date_de_vente = date_de_vente
			vente.produit_id = produit_id
			vente.commercial_id = commercial_id
			vente.client_id = client_id	

			vente.save_to_db()
			return vente.json()
		return {"message": "vente not found"}	
		

class VenteList(Resource):
	@jwt_optional
	def get(self):
		current_user_id = get_jwt_identity()

		vente = VenteModel.find_by_id(current_user_id)

		if not current_user_id:
			return {"message": "Veuillez vous connectez pour avoir accées avos données"}

		# if current_user_id != vente.user_id:
		# 	return {"message": "not found"}
			
		ventes = [x.json() for x in VenteModel.query.filter(VenteModel.user_id==current_user_id).all()]
		nombres_de_vente = len(ventes)

		# ventes_interval = [x.json() for x in VenteModel.query.filter(VenteModel.date_de_vente.between("2018-09-14","2020-09-14")).all()]

		return {
				"nombres_de_vente": nombres_de_vente,
				"ventes": ventes
			}, 200

class VenteStat(Resource):
	@jwt_required
	def get(self, date_debut, date_fin):
		current_user_id = get_jwt_identity()

		if not current_user_id:
			return {"message": "Veuillez-vous connectez"}
			
		vente_interval = VenteModel.query.filter(ProduitModel.prix_produit, VenteModel.date_de_vente.between(date_debut,date_fin)).all()
		nombre_vente_dict = {}

		best_product = (db.session.query(VenteModel.commercial_id, ProduitModel.product_name.label('name'),func.sum(ProduitModel.prix_produit).label("vtotal"))
								.join(ProduitModel, VenteModel.produit_id == ProduitModel.id)
								.join(CommercialModel, VenteModel.commercial_id == CommercialModel.id)
								.filter(VenteModel.date_de_vente.between(date_debut,date_fin))
								.group_by(VenteModel.commercial_id)
								.order_by(desc("vtotal")).limit(1).all())

		best_product_1 = []
		for row in best_product:
			best_product_1.append(row)

		qry = (db.session.query(VenteModel.commercial_id, CommercialModel.first_name, CommercialModel.last_name.label('name'),func.sum(ProduitModel.prix_produit).label("vtotal"))
								.join(ProduitModel, VenteModel.produit_id == ProduitModel.id)
								.join(CommercialModel, VenteModel.commercial_id == CommercialModel.id)
								.filter(VenteModel.date_de_vente.between(date_debut,date_fin))
								.group_by(VenteModel.commercial_id)
								.order_by(desc("vtotal")).limit(10).all())

		top_10_commerciaux = []
		for row in qry:
			top_10_commerciaux.append(row)

		vente_interval = [x.json() for x in VenteModel.query.filter(VenteModel.date_de_vente.between(date_debut,date_fin)).all()]
		nombre_vente_interval = len(vente_interval)

		return {
				"nombre_vente_interval": nombre_vente_interval,
				"vente_interval": vente_interval,
				"best_product_1": best_product_1,
				"top_10_commerciaux": top_10_commerciaux
			}