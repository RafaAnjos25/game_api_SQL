from flask import Flask, render_template, request, jsonify
from db import db
from models import Usuario
import os
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dados.db"
db.init_app(app)

@app.route('/registrar', methods=["Post"])
def registrar():
    data = request.get_json()

    if not data:
        os.abort("Error: Nenhum dado enviado"), 400
    
    campos_requeridos = ["nome", "email", "senha"]
    for campos in campos_requeridos:
        if campos not in data:
            return jsonify({"error": f"Campo obrigatório ausente: {campos}"}), 400

    try:         
        novo_usuario = Usuario(
            nome=data["nome"], 
            email=data["email"],
            senha=data["senha"])
        db.session.add(novo_usuario)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso"}), 201
    except Exception as e:
        return jsonify({"error: str(e)"}), 400

#@app.route('/deletar', methods=["Delete"])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
