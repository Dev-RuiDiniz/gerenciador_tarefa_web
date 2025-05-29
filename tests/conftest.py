# tests/conftest.py
import pytest
from app import app, db # Importa a instância do app e db do seu aplicativo principal
from models import User, Task # Importa os modelos

@pytest.fixture(scope='session') # O escopo 'session' significa que a fixture é executada uma vez por sessão de teste
def client():
    """
    Cria um cliente de teste do Flask para fazer requisições HTTP.
    Configura um banco de dados SQLite em memória para os testes.
    """
    app.config['TESTING'] = True
    # Usa um banco de dados SQLite em memória para testes
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False # Desativa CSRF para facilitar os testes de formulário

    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Cria as tabelas no banco de dados em memória
        yield client # Retorna o cliente de teste para os testes
        with app.app_context():
            db.drop_all() # Remove as tabelas após a execução dos testes