from db import db

class ClientModel(db.Model):
	__tablename__ = 'clients'
	
	id = db.Column(db.Integer, primary_key=True)
	denomination = db.Column(db.String(80), nullable=False)
	type_client = db.Column(db.String(80), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	ad_postale = db.Column(db.String(120), nullable=False)
	tel = db.Column(db.String(25), unique=True, nullable=False)
	name_interloc = db.Column(db.String(125), nullable=False)
	contact_interloc = db.Column(db.String(25), nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('UserModel')

	ventes = db.relationship('VenteModel', lazy='dynamic')

	def __init__(self, denomination, type_client, email, ad_postale, tel, name_interloc, contact_interloc, user_id):
		self.denomination = denomination
		self.type_client = type_client
		self.email = email
		self.ad_postale = ad_postale
		self.tel = tel
		self.name_interloc = name_interloc
		self.contact_interloc = contact_interloc
		self.user_id = user_id

	def json(self):
		return {
			'id': self.id,
			'denomination': self.denomination,
			'type_client': self.type_client,
			'email': self.email,
			'ad_postale': self.ad_postale,
			'tel': self.tel,
			'name_interloc': self.name_interloc,
			'contact_interloc': self.contact_interloc
		}

	
	@classmethod
	def find_by_id(cls, id):
		return cls.query.filter_by(id=id).first()

	@classmethod
	def find_by_email(cls, email):
		return cls.query.filter_by(email=email).first()

	@classmethod
	def find_by_tel(cls, tel):
		return cls.query.filter_by(tel=tel).first()	

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()
