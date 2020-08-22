from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#inicialização de flask e algumas chaves de segurança, o código ali inserido foi gerado aleatóriamente pela função hash do python 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e59d86e807f40bafb20cca686aebdd04'
#essa configuração seta a localização do banco de dados, aqui é definido que é localmente um arquivo de saída com nome 'site.db' no mesmo repositório deste __init__.py
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 2
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

#criação da variável que acessa o banco de dados
db = SQLAlchemy(app)

#esse import precisa ser feito aqui embaixo, para evitar referências cíclicas, ref[a definir]
from flaskapp import routes
