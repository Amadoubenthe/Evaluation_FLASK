from datetime import date
from db import db

import datetime

class CommercialModel(db.Model):
	__tablename__ = 'commercials'

	id = db.Column(db.Integer, primary_key=True)
	last_name = db.Column(db.String(32), nullable=False)
	first_name = db.Column(db.String(100), nullable=False)
	date_emb = db.Column(db.DateTime(), default=datetime, nullable=False)
	matricule = db.Column(db.String(80), unique=True, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('UserModel')

	ventes = db.relationship('VenteModel', lazy='dynamic')

	def __init__(self, last_name, first_name, date_emb, matricule, user_id):
		self.last_name = last_name
		self.first_name = first_name
		self.date_emb = date_emb
		self.matricule = matricule
		self.user_id = user_id

	def json(self):
		return {
			'id': self.id,
			'last_name': self.last_name,
			'first_name': self.first_name,
			'date_emb': self.date_emb.strftime('%Y-%m-%d'),
			'matricule': self.matricule,
			'user_id': self.user_id
		}
		

	@classmethod
	def find_by_id(cls, id):
		return cls.query.filter_by(id=id).first()

	@classmethod
	def find_by_user_id(cls, user_id):
		return cls.query.filter_by(user_id=user_id).first()		

	@classmethod
	def find_by_matricule(cls, matricule):
		return cls.query.filter_by(matricule=matricule).first()		

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()
	