# tests/conftest.py
import pytest
from app import app
from extensions import db
from models import User, Task
from flask_login import current_user # Importar aqui para usar no contexto do fixture

@pytest.fixture(scope='function')
def client():
    """
    Cria um cliente de teste do Flask e configura um banco de dados SQLite em memória
    que é recriado para CADA FUNÇÃO DE TESTE.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False # Desativa CSRF para facilitar os testes de formulário

    with app.app_context(): # Um único contexto de aplicação para setup/teardown do DB
        db.create_all()
        # O cliente de teste é gerado dentro deste contexto, mas opera em seu próprio contexto de requisição
        yield app.test_client() # Retorna o cliente de teste para os testes
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def logged_in_user_id(client):
    """
    Registra um usuário, faz login e retorna seu ID.
    O login é persistido na sessão do cliente de teste para o ciclo de vida do teste.
    """
    with app.app_context(): # Usar app_context para criar o usuário no DB
        user = User(username='loggedtestuser', email='logged@example.com')
        user.set_password('loggedpass')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Faz o login usando o cliente de teste. Isso modifica o estado da sessão do cliente.
    login_response = client.post('/auth/login', data={
        'email': 'logged@example.com',
        'password': 'loggedpass'
    }, follow_redirects=True)

    assert "Login bem-sucedido!" in login_response.data.decode('utf-8')

    # Retorna o ID do usuário. O 'client' (que está logado) é passado implicitamente para o teste.
    return user_id # Não 'yield', pois o login deve persistir durante o teste.