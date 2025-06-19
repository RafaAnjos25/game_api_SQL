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
        return jsonify({"ERROR": "Nenhum dado enviado"}), 400
    
    campos_requeridos = ["nome", "email", "senha"]
    for campos in campos_requeridos:
        if campos not in data:
            return jsonify({"ERROR": f"Campo obrigatório ausente: {campos}"}), 400

    try:         
        novo_usuario = Usuario(
            nome=data["nome"], 
            email=data["email"],
            senha=data["senha"])
        db.session.add(novo_usuario)
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso"}), 201
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400
    
@app.route('/editar/<int:id>', methods=["PUT"])
def editar(id):
    try:
        editar_usuario = db.session.query(Usuario).filter_by(id=id).first()  
        data = request.get_json()

        if not data:
            return jsonify({"ERROR": "Nenhum dado enviado"}), 400
        if editar_usuario.query.filter_by(nome=data["nome"]).first():
            return jsonify({"ERROR": "Nome já existe"}), 400
        if editar_usuario.query.filter_by(email=data["email"]).first():
            return jsonify({"ERROR": "Email já cadastrado"}), 400

        editar_usuario.nome=data["nome"]
        editar_usuario.email=data["email"]
        editar_usuario.senha=data["senha"]       
        db.session.commit()
        return jsonify({"message": "Usuário atualizado com sucesso"}), 201
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400

@app.route('/deletar', methods=["Delete"])
def deletar():
    data = request.get_json()
    if not data:
        return jsonify({"ERROR": "Nenhum dado enviado"}), 400
    
    try:
        deletar_usuario = db.session.execute(db.select(Usuario).filter_by(id=data["id"])).scalar_one()
        db.session.delete(deletar_usuario)
        db.session.commit()
        return jsonify({"message": "Usuário deletado com sucesso"}), 201
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400

@app.route('/obter', methods=["GET"])
def obter():
        data = request.get_json()
        if not data:
            try:
                usuarios = db.session.execute(db.select(Usuario).order_by(Usuario.nome)).scalars()
                resultado = [{'nome': usuario.nome, 'email': usuario.email} for usuario in usuarios]
                return jsonify(resultado),200
            except Exception as e:
                return jsonify({"ERROR": str(e)}), 500
        else:
            try:
                usuarios = db.session.execute(db.select(Usuario).filter_by(id=data["id"])).scalar_one()
                resultado = [{'nome': usuarios.nome, 'email': usuarios.email}]
                return jsonify(resultado),200
            except Exception as e:
                return jsonify({"ERROR": "Usuário não encontrado"}), 404
        

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
