from flask import Flask, request, redirect
from auth import get_authorization_url, exchange_code_for_token
from database import initialize_database
from data_processing import save_activities_to_db

import time

app = Flask(__name__)

@app.route('/')
def index():
    url = get_authorization_url("http://127.0.0.1:5000/authorization")
    return redirect(url)

@app.route('/authorization')
def authorization():
    code = request.args.get('code')
    
    exchange_code_for_token(code)
    initialize_database()
    save_activities_to_db()
    return 'Dados atualizados com sucesso! Você já pode fechar essa janela.'

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=10000) # deploy
    app.run(debug=True)