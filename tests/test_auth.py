# tests/test_auth.py
import pytest
from app import db # Ou from extensions import db, dependendo da sua estrutura
from models import User
from werkzeug.security import generate_password_hash
from flask_login import current_user # Importar aqui para usar no contexto do app

# A fixture 'client' é fornecida por conftest.py
def register_user(client, username, email, password):
    """Função auxiliar para registrar um usuário."""
    return client.post('/auth/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password
    }, follow_redirects=True)

def login_user(client, email, password):
    """Função auxiliar para logar um usuário."""
    return client.post('/auth/login', data={
        'email': email,
        'password': password
    }, follow_redirects=True)

def test_register_page_loads(client):
    """Testa se a página de registro carrega corretamente."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert "Registrar" in response.data.decode('utf-8')

def test_login_page_loads(client):
    """Testa se a página de login carrega corretamente."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert "Login" in response.data.decode('utf-8')

def test_register_user_success(client):
    """Testa o registro bem-sucedido de um novo usuário."""
    response = register_user(client, 'testuser', 'test@example.com', 'password123')
    # Corrigindo a asserção da mensagem flash
    assert "Sua conta foi criada com sucesso!" in response.data.decode('utf-8')
    assert "Agora você pode fazer login." in response.data.decode('utf-8')
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'

def test_register_existing_username(client):
    """Testa o registro com um nome de usuário já existente."""
    register_user(client, 'existinguser', 'email1@example.com', 'password123')
    response = register_user(client, 'existinguser', 'email2@example.com', 'password456')
    # Corrigindo a asserção da mensagem flash
    assert "Esse nome de usuário já está em uso." in response.data.decode('utf-8')
    with client.application.app_context():
        assert User.query.filter_by(username='existinguser').count() == 1

def test_register_existing_email(client):
    """Testa o registro com um e-mail já existente."""
    register_user(client, 'user1', 'existing@example.com', 'password123')
    response = register_user(client, 'user2', 'existing@example.com', 'password456')
    # Corrigindo a asserção da mensagem flash
    assert "Esse email já está registrado." in response.data.decode('utf-8')
    with client.application.app_context():
        assert User.query.filter_by(email='existing@example.com').count() == 1

def test_login_user_success(client):
    """Testa o login bem-sucedido de um usuário."""
    register_user(client, 'loginuser', 'login@example.com', 'loginpass')
    
    with client:
        response = login_user(client, 'login@example.com', 'loginpass')
        assert "Login bem-sucedido!" in response.data.decode('utf-8')
        assert "Bem-vindo ao seu Gerenciador de Tarefas!" in response.data.decode('utf-8')

        # current_user disponível aqui
        assert current_user.is_authenticated
        assert current_user.username == 'loginuser'


def test_login_invalid_password(client):
    """Testa o login com senha incorreta."""
    register_user(client, 'userpass', 'userpass@example.com', 'correctpass')

    with client:
        response = login_user(client, 'userpass@example.com', 'wrongpass')
        assert "Login falhou. Por favor, verifique seu email e senha." in response.data.decode('utf-8')

        assert not current_user.is_authenticated


def test_login_non_existent_email(client):
    """Testa o login com um e-mail não registrado."""
    with client:
        response = login_user(client, 'nonexistent@example.com', 'anypass')
        assert "Login falhou. Por favor, verifique seu email e senha." in response.data.decode('utf-8')
        assert not current_user.is_authenticated

def test_logout_user(client):
    """Testa o logout de um usuário."""
    with client:
        register_user(client, 'logoutuser', 'logout@example.com', 'logoutpass')
        login_user(client, 'logout@example.com', 'logoutpass')
        response = client.get('/auth/logout', follow_redirects=True)
        assert "Você foi desconectado." in response.data.decode('utf-8')
        assert not current_user.is_authenticated

def test_protected_route_redirects_to_login(client):
    """Testa se uma rota protegida redireciona para o login quando deslogado."""
    response = client.get('/tasks', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']