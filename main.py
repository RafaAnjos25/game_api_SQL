from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user
import hashlib
from db import db
from models import Usuario, Ranking
from sqlalchemy import create_engine

app = Flask(__name__)
app.secret_key = 'espectro'
lm = LoginManager(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dados.db"
db.init_app(app)

def hash(txt):
    hash_obj = hashlib.sha256(txt.encode('utf-8'))
    return hash_obj.hexdigest()

@lm.user_loader
def user_loader(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario

@app.route('/login', methods=['Post'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"ERROR": "Nenhum dado enviado"}), 400

    campos_requeridos = ["nome", "senha"]
    for campos in campos_requeridos:
        if campos not in data:
            return jsonify({"ERROR": f"Campo obrigatório ausente: {campos}"}), 400

    try:
        nome=data["nome"]
        senha=data["senha"]

        usuario = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
        if not usuario:
            return jsonify({"ERROR": "Nome ou senha incorretos"}), 400

        login_user(usuario)
        return jsonify({"message": f"Olá {nome}, seja bem vindo"})
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400
    
@app.route('/logout', methods=['Post'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Usuário deslogado com sucesso"})
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400

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
            senha=hash(data["senha"]))
        novo_ranking = Ranking(
            nome=data["nome"]
        )
        db.session.add(novo_usuario)
        db.session.add(novo_ranking)
        db.session.commit()
        login_user(novo_usuario)
        return jsonify({"message": "Usuário cadastrado com sucesso"}), 201
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400
    
@app.route('/editar/<int:id>', methods=["PUT"])
@login_required
def editar(id):
    try:
        editar_usuario = db.session.query(Usuario).filter_by(id=id).first()
        ran_editar_usuario = db.session.query(Ranking).filter_by(id=id).first()
        data = request.get_json()

        if not data:
            return jsonify({"ERROR": "Nenhum dado enviado"}), 400
        if editar_usuario.query.filter_by(nome=data["nome"]).first():
            return jsonify({"ERROR": "Nome já existe"}), 400
        if editar_usuario.query.filter_by(email=data["email"]).first():
            return jsonify({"ERROR": "Email já cadastrado"}), 400

        ran_editar_usuario.nome=data["nome"]
        editar_usuario.nome=data["nome"]
        editar_usuario.email=data["email"]
        editar_usuario.senha=hash(data["senha"])       
        db.session.commit()
        return jsonify({"message": "Usuário atualizado com sucesso"}), 201
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400

@app.route('/deletar', methods=["Delete"])
@login_required
def deletar():
    data = request.get_json()
    if not data:
        return jsonify({"ERROR": "Nenhum dado enviado"}), 400
    
    try:
        deletar_usuario = db.session.execute(db.select(Usuario).filter_by(id=data["id"])).scalar_one()
        rank_deletar_usuario = db.session.execute(db.select(Ranking).filter_by(id=data["id"])).scalar_one()
        db.session.delete(deletar_usuario)
        db.session.delete(rank_deletar_usuario)
        db.session.commit()
        return jsonify({"message": "Usuário deletado com sucesso"}), 201
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400

@app.route('/obter', methods=["GET"])
@login_required
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
        
@app.route('/conquista', methods=['PUT'])
@login_required
def tempo_conquista():
    data = request.get_json()
    if not data:
        return jsonify({"ERROR": "Nenhum dado enviado"})
    
    tempo = data["tempo"]
    if tempo <= 1:
        return jsonify({"Conquista desbloqueada": "Mister Sonico - terminou em um minuto ou menos"})
    elif tempo > 1 and data["tempo"] <= 5:
        return jsonify({"Conquista desbloqueada": "Uno de escada - terminou entre 1 e 5 minutos"})
    elif tempo > 10:
        return jsonify({"Conquista desbloqueada": "Tartaruga sem perna - terminou em mais de 10 minutos"})
    else:
        return jsonify({"message": "Terminou"})
            

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
