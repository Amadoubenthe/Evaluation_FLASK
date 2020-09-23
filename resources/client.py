from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity, jwt_optional, fresh_jwt_required
from models.client import ClientModel

import re

import datetime

class Client(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('denomination',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('type_client',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('email',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('ad_postale',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)
	parser.add_argument('tel',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('name_interloc',
						type=str,
						required=True,
						nullable=False,
						help="This field cannot be left blank!"
						)

	parser.add_argument('contact_interloc',
						type=str,
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
	@jwt_optional
	def get(self, id):
		current_user_id = get_jwt_identity()
		client = ClientModel.find_by_id(id)

		if client:
			if client.user_id == current_user_id:
				return client.json()

			return {"message": "Veuillez vous connectez"}	

		return {'message': 'Client not found'}, 404		

	@jwt_required	
	def post(self):
		data = Client.parser.parse_args()
		if ClientModel.find_by_email(data['email']):
			return {'message': "A Client with that email already exists."}, 400

		if ClientModel.find_by_tel(data['tel']):
			return {'message': "A Client with that number already exists."}, 400	

		denomination = data['denomination']
		if not denomination:
			return {'message': "Veuilez entrer la denomination de l'entreprise"}	

		type_client = data['type_client']
		if not type_client:
			return {'message': "Veuilez entrer le type de client"}
			
		email = data['email']
		if not email:
			return {'message': "Veuilez entrer le mail du client"}
		match = re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)
		if not match:
			return {"message": "Movaise adresse mail"}

		ad_postale = data['ad_postale']
		if not ad_postale:
			return {'message': "Veuilez entrer l'adresse postale du client"}

		tel = data['tel']
		if not tel:
			return {'message': "Veuilez entrer le numero de telephone du client"}

		name_interloc = data['name_interloc']
		if not name_interloc:
			return {'message': "Veuilez entrer le nom  de l'interlocuteur"}

		contact_interloc = data['contact_interloc']
		if not contact_interloc:
			return {'message': "Veuilez entrer le contact de l'interlocuteur"}
			
		client = ClientModel(**data)
		try:
			client.save_to_db()
		except:
			return {"message": "An error occurred creating the client."}, 500

		return client.json(), 201

	@jwt_required	
	def delete(self, id):
		current_user_id = get_jwt_identity()
		if current_user_id:
			client = ClientModel.find_by_id(id)
			if client and client.user_id == current_user_id:
				client.delete_from_db()
				return {'message': 'Client deleted'}
			return {'message': 'Client not found.'}, 404

		return {"message": "Veuillez vous connectez"}

	@jwt_required
	def put(self, id):
		current_user_id = get_jwt_identity()
		if current_user_id:
			data = Client.parser.parse_args()
			client = ClientModel.find_by_id(id)
			if client and client.user_id == current_user_id:
				denomination = data['denomination']
				if not denomination:
					return {'message': "Veuillez entrer la denomination"}

				type_client = data['type_client']
				if not type_client:
					return {'message': "Veuillez entrer le type de client"}

				ad_postale = data['ad_postale']
				if not ad_postale:
					return {'message': "Veuillez entrer l'adresse postale du client"}

				tel = data['tel']
				if not tel:
					return {"message": "Veuillez entrez le numero du client"}

				name_interloc = data['name_interloc']
				if not name_interloc:
					return {"message": "Veuillez entrez le nom de l'interlocuteur"}

				contact_interloc = data['contact_interloc']
				if not contact_interloc:
					return {"message": "Veuillez entrez le contact de l'interlocuteur"}

				tel = data['tel']
				if not tel:
					return {"message": "Veuillez entrer votre numero de telephone"}

				if ClientModel.find_by_tel(tel):
					return {"message": "Ce numero existe deja"}


				client.denomination = denomination
				client.type_client = type_client
				client.ad_postale = ad_postale
				client.tel = tel
				client.name_interloc = name_interloc
				client.contact_interloc = contact_interloc

				client.save_to_db()
				return client.json()

			return {"message": "Client not found"}, 400

		return {"message": "Veuillez vous connectez"}	

	
class ClientList(Resource):
	@jwt_optional
	def get(self):
		user_id = get_jwt_identity()
		if user_id:
			clients = [x.json() for x in ClientModel.query.filter(ClientModel.user_id==user_id).all()]
			nombre_client = len(clients)
			return {'nombre_client': nombre_client,
					'clients': clients
				}, 200
		return {"message": "Veuillez vous connectez pour avoir accés a vos donées."}
