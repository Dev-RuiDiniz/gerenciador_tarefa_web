# tests/test_auth.py
import pytest
from app import db
from models import User
from werkzeug.security import generate_password_hash

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
    assert b"Registrar" in response.data

def test_login_page_loads(client):
    """Testa se a página de login carrega corretamente."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_register_user_success(client):
    """Testa o registro bem-sucedido de um novo usuário."""
    response = register_user(client, 'testuser', 'test@example.com', 'password123')
    assert b"Sua conta foi criada com sucesso!" in response.data
    assert b"Agora voc\xc3\xaa pode fazer login." in response.data # Mensagem com acento
    with client.application.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.email == 'test@example.com'

def test_register_existing_username(client):
    """Testa o registro com um nome de usuário já existente."""
    register_user(client, 'existinguser', 'email1@example.com', 'password123')
    response = register_user(client, 'existinguser', 'email2@example.com', 'password456')
    assert b"Esse nome de usu\xc3\xa1rio j\xc3\xa1 est\xc3\xa1 em uso." in response.data
    with client.application.app_context():
        # Deve haver apenas um usuário com 'existinguser'
        assert User.query.filter_by(username='existinguser').count() == 1

def test_register_existing_email(client):
    """Testa o registro com um e-mail já existente."""
    register_user(client, 'user1', 'existing@example.com', 'password123')
    response = register_user(client, 'user2', 'existing@example.com', 'password456')
    assert b"Esse email j\xc3\xa1 est\xc3\xa1 registrado." in response.data
    with client.application.app_context():
        # Deve haver apenas um usuário com 'existing@example.com'
        assert User.query.filter_by(email='existing@example.com').count() == 1

def test_login_user_success(client):
    """Testa o login bem-sucedido de um usuário."""
    register_user(client, 'loginuser', 'login@example.com', 'loginpass')
    response = login_user(client, 'login@example.com', 'loginpass')
    assert b"Login bem-sucedido!" in response.data
    # Após o login, o usuário deve ser redirecionado para a home
    assert b"Bem-vindo ao seu Gerenciador de Tarefas!" in response.data
    # Verifica se o current_user está autenticado
    with client.application.app_context():
        from flask_login import current_user
        assert current_user.is_authenticated

def test_login_invalid_password(client):
    """Testa o login com senha incorreta."""
    register_user(client, 'userpass', 'userpass@example.com', 'correctpass')
    response = login_user(client, 'userpass@example.com', 'wrongpass')
    assert b"Login falhou. Por favor, verifique seu email e senha." in response.data
    # Usuário não deve estar autenticado
    with client.application.app_context():
        from flask_login import current_user
        assert not current_user.is_authenticated

def test_login_non_existent_email(client):
    """Testa o login com um e-mail não registrado."""
    response = login_user(client, 'nonexistent@example.com', 'anypass')
    assert b"Login falhou. Por favor, verifique seu email e senha." in response.data
    with client.application.app_context():
        from flask_login import current_user
        assert not current_user.is_authenticated

def test_logout_user(client):
    """Testa o logout de um usuário."""
    register_user(client, 'logoutuser', 'logout@example.com', 'logoutpass')
    login_user(client, 'logout@example.com', 'logoutpass')
    response = client.get('/auth/logout', follow_redirects=True)
    assert b"Voc\xc3\xaa foi desconectado." in response.data
    with client.application.app_context():
        from flask_login import current_user
        assert not current_user.is_authenticated

def test_protected_route_redirects_to_login(client):
    """Testa se uma rota protegida redireciona para o login quando deslogado."""
    response = client.get('/tasks', follow_redirects=False) # Não seguir redirecionamento
    assert response.status_code == 302 # Espera um redirecionamento (302 Found)
    assert '/auth/login' in response.headers['Location']