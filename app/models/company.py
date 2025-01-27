from app import db
from datetime import datetime

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    razao_social = db.Column(db.String(255), nullable=False)
    nome_fantasia = db.Column(db.String(255))
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    status = db.Column(db.String(50))
    telefone1 = db.Column(db.String(20))
    telefone2 = db.Column(db.String(20))
    capital_social = db.Column(db.String(50))
    socios = db.Column(db.JSON)
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    neighborhood = db.Column(db.String(100))
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'razaoSocial': self.razao_social,
            'nomeFantasia': self.nome_fantasia,
            'cnpj': self.cnpj,
            'status': self.status,
            'telefone1': self.telefone1,
            'telefone2': self.telefone2,
            'capitalSocial': self.capital_social,
            'socios': self.socios,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'neighborhood': self.neighborhood,
            'email': self.email
        }