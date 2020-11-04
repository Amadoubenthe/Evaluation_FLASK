import json
import datetime
from json import JSONEncoder
from collections import Counter 
from db import db
import datetime
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity, jwt_optional, fresh_jwt_required
from models.commercial import CommercialModel

class Commercial(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('last_name',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('first_name',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('matricule',
						type=str,
						nullable=False,
						required=True,
						help="This field cannot be left blank!"
						)

	@jwt_required
	def get(self, id):
		current_user_id = get_jwt_identity()
		commercial = CommercialModel.find_by_id(id)
		
		if commercial:
			if current_user_id == commercial.user_id:
				return commercial.json()

			return {"message": "veuillez vous connectez."}

		return {'message': 'Commercial not found'}, 404	

	@jwt_required	
	def post(self):

		data = Commercial.parser.parse_args()

		if CommercialModel.find_by_matricule(data['matricule']):
			return {'message': "A Commercial with that matricule already exists."}, 400

		last_name = data['last_name']
		if not last_name:
			return {'message': "Veuilez entrer le nom"}

		first_name = data['first_name']
		if not first_name:
			return {'message': "Veuilez entrer le prénom"}

		matricule = data['matricule']
		if not matricule:
			return {'message': "Veuilez entrer le matricule"}	

		commercial = CommercialModel(data['last_name'], data['first_name'], data['matricule'])
		commercial.date_emb = datetime.datetime.now()
		commercial.user_id = get_jwt_identity()

		try:
			print(commercial.last_name)
			commercial.save_to_db()
		except:
			return {"message": "An error occurred creating the commercial."}, 500

		return commercial.json(), 201

	@jwt_required
	def delete(self, id):
		current_user_id = get_jwt_identity()
		commercial = CommercialModel.find_by_id(id)
		
		if commercial:
			if commercial.user_id == current_user_id:
				commercial.delete_from_db()
				return {'message': 'Commercial deleted'}

		return {'message': 'Commercial not found'}

	@jwt_required
	def put(self, id):

		data = Commercial.parser.parse_args()
		current_user_id = get_jwt_identity()

		commercial = CommercialModel.find_by_id(id)
		if commercial:
			if commercial.user_id == current_user_id:

				last_name = data['last_name']
				if not last_name:
					return {'message': "Veuilez entrer le nom"}
				
				first_name = data['first_name']
				if not first_name:
					return {'message': "Veuilez entrer le prénom"}
				
				date_emb = data['date_emb']
				if not date_emb:
					return {'message': "Veuilez entrer la date d'embauche"}

				matricule = data['matricule']
				if not matricule:
					return {'message': "Veuilez entrer le matricule"}
				if CommercialModel.find_by_matricule(data['matricule']):
					return {'message': "A Commercial with that matricule already exists."}, 400

				commercial.last_name = last_name
				commercial.first_name =first_name
				commercial.date_emb = date_emb
				commercial.matricule = matricule

				commercial.save_to_db()
				
				return commercial.json()

			return {"message": "veuillez vous connectez."}

		return {"message": "Commercial not found"}			

class CommercialList(Resource):
	@jwt_optional
	def get(self):

		current_user_id = get_jwt_identity()
		if current_user_id:
			commerciaux = [x.json() for x in CommercialModel.query.filter(CommercialModel.user_id==current_user_id).all()]
			nombre_commerciaux = len(commerciaux)
			return {'nombre_commerciaux': nombre_commerciaux,
					'commerciaux': commerciaux
				}, 200

		return{"message": "veuillez vous connectez pour avoir acces aux données"}
		