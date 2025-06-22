from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user
import hashlib
from db import db
from models import Usuario, Ranking, Conquistas

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
        return jsonify({"message": f"Olá {nome}, seja bem vindo"}),200
    except Exception as e:
        return jsonify({"ERROR": str(e)}), 400
    
@app.route('/logout', methods=['Post'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({"message": "Usuário deslogado com sucesso"}),200
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
        novo_conquista = Conquistas(
            nome=data["nome"]
        )   
        db.session.add(novo_usuario)
        db.session.add(novo_ranking)
        db.session.add(novo_conquista)
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
        con_editar_usuario = db.session.query(Conquistas).filter_by(id=id).first()
        data = request.get_json()

        if not data:
            return jsonify({"ERROR": "Nenhum dado enviado"}), 400
        if editar_usuario.query.filter_by(nome=data["nome"]).first():
            return jsonify({"ERROR": "Nome já existe"}), 400
        if editar_usuario.query.filter_by(email=data["email"]).first():
            return jsonify({"ERROR": "Email já cadastrado"}), 400

        ran_editar_usuario.nome=data["nome"]
        con_editar_usuario.nome=data["nome"]
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
        conq_deletar_usuario = db.session.execute(db.select(Conquistas).filter_by(id=data["id"])).scalar_one()
        db.session.delete(deletar_usuario)
        db.session.delete(rank_deletar_usuario)
        db.session.delete(conq_deletar_usuario)
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
                return jsonify({"ERROR": str(e)}), 400
        else:
            try:
                usuarios = db.session.execute(db.select(Usuario).filter_by(id=data["id"])).scalar_one()
                resultado = [{'nome': usuarios.nome, 'email': usuarios.email}]
                return jsonify(resultado),200
            except Exception as e:
                return jsonify({"ERROR": "Usuário não encontrado"}), 404
        
@app.route('/tempo/<int:id>', methods=['PUT'])
@login_required
def registrar_tempo(id):
    data = request.get_json()
    tempo_novo = data["tempo"]
    tempo_antigo = db.session.query(Ranking).filter_by(id=id).first()
    conquista = db.session.query(Conquistas).filter_by(id=id).first()

    if not data:
        try:
            return jsonify({"ERROR": "Nenhum dado enviado"})
        except Exception as e:
            return jsonify({"ERROR": str(e)}), 400
      
    if tempo_antigo.tempo is None or tempo_novo < tempo_antigo.tempo:
        try:
            tempo_antigo.tempo = data["tempo"]
            db.session.commit()
            if tempo_novo <= 1.00  and conquista.Conquista_1_minuto == False:
                conquista.Conquista_1_minuto = True
                db.session.commit()
                return jsonify({"Conquista desbloqueada": "Mister Sonico - terminou em um minuto ou menos"})
            elif tempo_novo > 1.00 and tempo_novo <= 5.00 and conquista.Conquista_5_minuto == False:
                conquista.Conquista_5_minuto = True
                db.session.commit()
                return jsonify({"Conquista desbloqueada": "Uno de escada - terminou entre 1 e 5 minutos"})
            elif tempo_novo > 10.00 and conquista.Conquista_10_minuto == False:
                conquista.Conquista_10_minuto = True
                db.session.commit()
                return jsonify({"Conquista desbloqueada": "Tartaruga sem perna - terminou em mais de 10 minutos"})
            else:
                return jsonify({"message": "Terminou"})
        except Exception as e:
            return jsonify({"ERROR": str(e)}), 400
    else:
        try:
            if tempo_novo <= 1.00  and conquista.Conquista_1_minuto == False:
                conquista.Conquista_1_minuto = True
                db.session.commit()
                return jsonify({"Conquista desbloqueada": "Mister Sonico - terminou em um minuto ou menos"})
            elif tempo_novo > 1.00 and tempo_novo <= 5.00 and conquista.Conquista_5_minuto == False:
                conquista.Conquista_5_minuto = True
                db.session.commit()
                return jsonify({"Conquista desbloqueada": "Uno de escada - terminou entre 1 e 5 minutos"})
            elif tempo_novo > 10.00 and conquista.Conquista_10_minuto == False:
                conquista.Conquista_10_minuto = True
                db.session.commit()
                return jsonify({"Conquista desbloqueada": "Tartaruga sem perna - terminou em mais de 10 minutos"})
            else:
                return jsonify({"message": "Terminou"})
        except Exception as e:
            return jsonify({"ERROR": str(e)}), 400    

@app.route('/ranking', methods=["GET"])
@login_required
def obter_ranking():
    data = request.get_json()
    if not data: 
        try:
            ranking = db.session.execute(db.select(Ranking).filter(Ranking.tempo!=None).order_by(Ranking.tempo)).scalars()
            resultado = [{'Posicao': i, 'nome': rank.nome, 'tempo': rank.tempo} for i, rank in enumerate(ranking, start=1)]    
            return jsonify(resultado),200
        except Exception as e:
            return jsonify({"ERROR": str(e)}), 400
    else:
        try:
            id_rank = data["id"]
            ranking = db.session.execute(db.select(Ranking).filter(Ranking.tempo!=None).order_by(Ranking.tempo)).scalars()
            for i, rank in enumerate(ranking, start=1):
                if rank.id == id_rank:
                    return jsonify ({'Posicao': i, 'nome': rank.nome, 'tempo': rank.tempo})        
            return jsonify({"ERROR": "Usuario não encontrado ou sem tempo"}), 404
        except Exception as e:
            return jsonify({"ERROR": str(e)}), 400
            
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
