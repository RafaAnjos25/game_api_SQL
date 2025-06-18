from flask import Flask, render_template, request, jsonify
from db import db
from models import Usuario
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///dados.db"
db.init_app(app)

@app.route('/registrar')
def registrar():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Nenhum dado enviado"}), 400
    
    campos_requeridos = ["nome", "email", "senha"]


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
