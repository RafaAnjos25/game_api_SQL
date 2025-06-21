from db import db
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    senha = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<{self.nome}"

class Ranking(db.Model):
    __tablename__ = 'Ranking'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), ForeignKey("Usuarios.nome", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    tempo = db.Column(db.Float)
    nome_usuario = relationship("Usuario", foreign_keys=[nome])

    def __repr__(self):
        return f"<{self.nome}"
    
         
