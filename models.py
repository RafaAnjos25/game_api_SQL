from db import db

class Usuario(db.Model):
    __tablename__ = 'Usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(40), nullable=False, unique=True)
    senha = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<{self.nome}"