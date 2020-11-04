from db import db
import datetime

class ProduitModel(db.Model):
	__tablename__='produits'
	
	id = db.Column(db.Integer, primary_key=True)
	product_name = db.Column(db.String(100), nullable=False)
	desc = db.Column(db.String(250), nullable=False)
	date_mise_vente = db.Column(db.DateTime(), default=datetime, nullable=False)
	status = db.Column(db.String(20), nullable=False)
	type_produit = db.Column(db.String(10), nullable=False)
	code = db.Column(db.String(80), unique=True, nullable=False)

	prix_produit = db.Column(db.Float(precision=2))

	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('UserModel')

	ventes = db.relationship('VenteModel', lazy='dynamic')

	def __init__(self, product_name, desc, status, type_produit, code, prix_produit):
		self.product_name = product_name
		self.desc = desc
		self.status = status
		self.type_produit = type_produit
		self.code = code
		self.prix_produit = prix_produit

	def json(self):
		return {
			'id': self.id,
			'product_name': self.product_name,
			'desc': self.desc,
			'date_mise_vente': self.date_mise_vente.strftime('%Y-%m-%d'),
			'status': self.status,
			'type_produit': self.type_produit,
			'prix_produit': self.prix_produit,
			'code': self.code,
		}

	@classmethod
	def find_by_code(cls, code):
		return cls.query.filter_by(code=code).first()

	@classmethod
	def find_by_id(cls, id):
		return cls.query.filter_by(id=id).first()	

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()
	