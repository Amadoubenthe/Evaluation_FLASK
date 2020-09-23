from db import db


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    commercials = db.relationship('CommercialModel', lazy='dynamic')

    produits = db.relationship('ProduitModel', lazy='dynamic')

    clients = db.relationship('ClientModel', lazy='dynamic')

    ventes = db.relationship('VenteModel', lazy='dynamic')
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        # self.password = Bcrypt.generate_password_hash(password)

    def json(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username
        }
            
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()    

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()