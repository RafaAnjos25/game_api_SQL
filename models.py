from db import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    senha = db.Column(db.String(20), nullable=False)

class Ranking(db.Model):
    __tablename__ = 'Ranking'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False, unique=True)
    tempo = db.Column(db.Float)

    def __repr__(self):
        return f"<{self.nome}"