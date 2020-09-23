from datetime import datetime
from datetime import date

from db import db

class VenteModel(db.Model):
	__tablename__ = 'ventes'


	id = db.Column(db.Integer, primary_key=True)

	date_de_vente = db.Column(db.Date(), nullable=False)


	produit_id = db.Column(db.Integer, db.ForeignKey('produits.id'))
	produit = db.relationship('ProduitModel')

	commercial_id = db.Column(db.Integer, db.ForeignKey('commercials.id'))
	commercial = db.relationship('CommercialModel')

	client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
	client = db.relationship('ClientModel')

	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('UserModel')

	def __init__(self, date_de_vente, produit_id, commercial_id, client_id, user_id):
		self.date_de_vente = date_de_vente
		self.produit_id = produit_id
		self.commercial_id = commercial_id
		self.client_id = client_id
		self.user_id = user_id

	
	def json(self):
		return {
				'id': self.id,
				'date_de_vente': self.date_de_vente.strftime('%Y-%m-%d'),
				'produit_id': self.produit_id,
				'commercial_id': self.commercial_id,
				'client_id': self.client_id
			}

	@classmethod
	def find_by_id(cls, _id):
		return cls.query.filter_by(id=_id).first()

	
	@classmethod
	def find_by_id(cls, id):
		return cls.query.filter_by(id=id).first()


	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()	
		