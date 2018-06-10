from flask import Flask, render_template, request, redirect, session, flash, url_for
from dao_modified import JogoDao, UsuarioDao
from flask_mysqldb import MySQL
from models_modified import Jogo, Usuario


app = Flask(__name__)
app.secret_key = 'app_test'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "1905527Rr"
app.config['MYSQL_DB'] = "jogoteca_md"
app.config['MYSQL_PORT'] = 3306

db = MySQL(app)
jogo_dao = JogoDao(db)
usuario_dao = UsuarioDao(db)


@app.route('/')
def index():
    lista = jogo_dao.listar()
    return render_template('lista_md.html', titulo='Jogos', jogos=lista)


@app.route('/novo')
def novo():
    if not verify():
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo_md.html', titulo='Novo Jogo')


@app.route('/criar', methods=['POST',])
def criar():
    dados = get_dados()
    jogo = Jogo(dados[0],dados[1],dados[2])
    jogo_dao.salvar(jogo)
    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    jogo = jogo_dao.busca_por_id(id)
    if not verify():
        flash('É necessário logar para editar os Jogos! ;D')
        return redirect(url_for('login', proxima=url_for('editar', id=jogo.id)))
    return render_template('edit_md.html', jogo=jogo, titulo='Editando Jogo')

@app.route('/atualizar/<int:id>',methods=['POST',])
def atualizar(id):
    dados = get_dados()
    jogo = Jogo(dados[0],dados[1],dados[2], id)
    jogo_dao.salvar(jogo)
    return redirect(url_for('index'))

@app.route('/deletar/<int:id>', methods=['POST','GET'])
def deletar(id):
    if not verify():
        flash('É necessário logar! ;D')
        return redirect(url_for('login', proxima=url_for('deletar', id=id)))
    jogo = jogo_dao.busca_por_id(id)
    jogo_dao.deletar(jogo.id)
    return redirect(url_for('index'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login_md.html', proxima=proxima)

@app.route('/autenticar', methods=['POST',])
def autenticar():
    usuario = usuario_dao.buscar_por_id(request.form['usuario'])
    print(usuario)
    if usuario:
        if usuario.senha == request.form['senha']:

            session['usuario_logado'] = usuario.id
            flash(usuario.nome + ' logou com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    else:
        flash('Não logado, tente denovo!')
        return redirect(url_for('login'))

@app.route('/user', methods=['POST', 'GET'])
def user():
    return render_template('new_user_md.html', titulo='Novo Usuário')

@app.route('/new_user', methods=['POST', 'GET'])
def new_user():                     #Cria um novo usuário
    dados = get_dados_usuario()
    print(dados)
    user = Usuario(dados[0], dados[1], dados[2])
    if usuario_dao.salvar(user):
        flash('Usuário criado com sucesso!')
        return redirect(url_for('index'))
    else:                           #O else foi posto somente para melhorar a legibilidade
        flash('Este usuário já existe!')
        return redirect(url_for('new_user'))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('index'))

def get_dados_usuario():            #Pega os dados do usuário para a criação de um novo
    id = request.form['id']
    nome = request.form['nome']
    senha = request.form['senha']
    dados = (id, nome, senha)
    return dados

def get_dados():                    #Pega os dados de um jogo
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    dados = (nome, categoria, console)
    return dados

def verify():                       #Verifica se um usuário está logado
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return False
    return True


app.run(debug=True)