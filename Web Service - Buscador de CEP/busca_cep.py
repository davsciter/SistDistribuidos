from flask import Flask, render_template, request, flash
import os
import requests
from datetime import timedelta
from models import CEP
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days = 7)

lista = []
ceps = {}

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('buscar.html', titulo = 'Buscador ViaCEP', ceps = lista)

@app.route('/buscar', methods=['POST', ])
def buscar():
    cep = request.form['cep']
    url = f'https://viacep.com.br/ws/{cep}/json/'
    resposta = requests.request('GET', url)
    conteudo = resposta.content.decode('utf-8')
    resposta.close()
    endereco = json.loads(conteudo)

    if 'erro' not in endereco:
        if endereco['cep'] not in ceps:
            novo_cep = CEP(endereco['cep'], endereco['logradouro'], endereco['bairro'], endereco['localidade'], endereco['uf'], endereco['ibge'], endereco['ddd'], endereco['siafi'])
            lista.append(novo_cep)
            ceps[endereco['cep']] = 0

        for index, item in enumerate(lista):
            if item.cep == endereco['cep']:
                lista[index].addBusca()
                lista.append(lista.pop(index))
                break
        flash("CEP identificado com sucesso!", "alert alert-success")
        return render_template('resultado.html', titulo = 'Resultado da Busca', cep = endereco)
        
    else:
        flash('CEP não encontrado!', "alert alert-danger")
        return render_template('buscar.html', titulo = 'Buscador ViaCEP', ceps = lista)


if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
