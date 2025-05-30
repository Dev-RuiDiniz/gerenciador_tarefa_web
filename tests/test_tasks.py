# tests/test_tasks.py
import pytest
from app import app  # Importe app para poder acessar o app_context e current_user
from extensions import db  # Ou from app import db
from models import User, Task
from datetime import datetime
from flask_login import current_user

# Importa as funções auxiliares de auth
from tests.test_auth import register_user, login_user

# logged_in_user_id vem de conftest.py
# @pytest.fixture def logged_in_user(client): ... (Esta fixture será removida, use logged_in_user_id)

def create_task_via_form(client, title, description, due_date, status):
    """Função auxiliar para criar uma tarefa via formulário."""
    return client.post('/tasks/new', data={
        'title': title,
        'description': description,
        'due_date': due_date,
        'status': status
    }, follow_redirects=True)

def test_list_tasks_page_loads(client, logged_in_user_id):  # Usar a nova fixture
    """Testa se a página de listagem de tarefas carrega para um usuário logado."""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert "Minhas Tarefas" in response.data.decode('utf-8')

def test_create_task_success(client, logged_in_user_id):  # Usar a nova fixture
    """Testa a criação bem-sucedida de uma tarefa."""
    response = create_task_via_form(client, 'Tarefa de Teste', 'Descricao da tarefa', '2025-12-31', 'pendente')
    assert "Tarefa criada com sucesso!" in response.data.decode('utf-8')
    assert "Minhas Tarefas" in response.data.decode('utf-8')

    with app.app_context():  # Usar app.app_context() para interagir com o DB
        task = Task.query.filter_by(title='Tarefa de Teste').first()
        assert task is not None
        assert task.description == 'Descricao da tarefa'
        assert task.status == 'pendente'
        assert task.author.id == logged_in_user_id  # Comparar com o ID do usuário

def test_view_task_details(client, logged_in_user_id):  # Usar a nova fixture
    """Testa a visualização dos detalhes de uma tarefa."""
    with app.app_context():  # Usar app.app_context() para interagir com o DB
        user = User.query.get(logged_in_user_id)  # Obter o user pelo ID
        new_task = Task(title='Ver Detalhes', description='Detalhes importantes',
                        due_date=datetime(2025, 11, 15).date(), status='pendente', author=user)
        db.session.add(new_task)
        db.session.commit()
        task_id = new_task.id

    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    assert "Ver Detalhes" in response.data.decode('utf-8')
    assert "Detalhes importantes" in response.data.decode('utf-8')

def test_view_non_existent_task(client, logged_in_user_id):  # Usar a nova fixture
    """Testa a visualização de uma tarefa inexistente."""
    response = client.get('/tasks/99999')
    assert response.status_code == 404

def test_edit_task_success(client, logged_in_user_id):  # Usar a nova fixture
    """Testa a edição bem-sucedida de uma tarefa."""
    with app.app_context():  # Usar app.app_context() para interagir com o DB
        user = User.query.get(logged_in_user_id)  # Obter o user pelo ID
        task_to_edit = Task(title='Tarefa Antiga', description='Desc. Antiga',
                            due_date=datetime(2025, 1, 1).date(), status='pendente', author=user)
        db.session.add(task_to_edit)
        db.session.commit()
        task_id = task_to_edit.id

    response = client.post(f'/tasks/{task_id}/edit', data={
        'title': 'Tarefa Nova',
        'description': 'Desc. Nova',
        'due_date': '2025-02-01',
        'status': 'concluida'
    }, follow_redirects=True)

    assert "Tarefa atualizada com sucesso!" in response.data.decode('utf-8')
    assert "Tarefa Nova" in response.data.decode('utf-8')

    with app.app_context():  # Usar app.app_context() para interagir com o DB
        updated_task = Task.query.get(task_id)
        assert updated_task.title == 'Tarefa Nova'
        assert updated_task.description == 'Desc. Nova'
        assert updated_task.status == 'concluida'
        # Corrigido: converter para .date() para comparar data sem tempo
        assert updated_task.due_date.date() == datetime(2025, 2, 1).date()

def test_delete_task_success(client, logged_in_user_id):  # Usar a nova fixture
    """Testa a exclusão bem-sucedida de uma tarefa."""
    with app.app_context():  # Usar app.app_context() para interagir com o DB
        user = User.query.get(logged_in_user_id)  # Obter o user pelo ID
        task_to_delete = Task(title='Tarefa para Deletar', description='Delete-me',
                              due_date=datetime(2025, 3, 3).date(), status='pendente', author=user)
        db.session.add(task_to_delete)
        db.session.commit()
        task_id = task_to_delete.id

    response = client.post(f'/tasks/{task_id}/delete', follow_redirects=True)
    assert "Tarefa excluída com sucesso!" in response.data.decode('utf-8')
    assert "Minhas Tarefas" in response.data.decode('utf-8')

    with app.app_context():  # Usar app.app_context() para interagir com o DB
        assert Task.query.get(task_id) is None

def test_complete_task_success(client, logged_in_user_id):  # Usar a nova fixture
    """Testa a marcação de uma tarefa como concluída."""
    with app.app_context():  # Usar app.app_context() para interagir com o DB
        user = User.query.get(logged_in_user_id)  # Obter o user pelo ID
        task_to_complete = Task(title='Tarefa Incompleta', description='Completar agora',
                                due_date=datetime(2025, 4, 4).date(), status='pendente', author=user)
        db.session.add(task_to_complete)
        db.session.commit()
        task_id = task_to_complete.id

    response = client.post(f'/tasks/{task_id}/complete', follow_redirects=True)
    assert "Tarefa marcada como concluída!" in response.data.decode('utf-8')
    assert "Minhas Tarefas" in response.data.decode('utf-8')

    with app.app_context():  # Usar app.app_context() para interagir com o DB
        completed_task = Task.query.get(task_id)
        assert completed_task.status == 'concluida'

def test_uncomplete_task_success(client, logged_in_user_id):  # Usar a nova fixture
    """Testa a marcação de uma tarefa como pendente novamente."""
    with app.app_context():  # Usar app.app_context() para interagir com o DB
        user = User.query.get(logged_in_user_id)  # Obter o user pelo ID
        task_to_uncomplete = Task(title='Tarefa Completa', description='Revert',
                                  due_date=datetime(2025, 5, 5).date(), status='concluida', author=user)
        db.session.add(task_to_uncomplete)
        db.session.commit()
        task_id = task_to_uncomplete.id

    response = client.post(f'/tasks/{task_id}/uncomplete', follow_redirects=True)
    assert "Tarefa marcada como pendente novamente!" in response.data.decode('utf-8')
    assert "Minhas Tarefas" in response.data.decode('utf-8')

    with app.app_context():  # Usar app.app_context() para interagir com o DB
        uncompleted_task = Task.query.get(task_id)
        assert uncompleted_task.status == 'pendente'

def test_task_authorization(client, app):
    """Testa que um usuário não pode acessar/modificar tarefas de outro usuário."""

    with app.app_context():
        user_a = User(username='userA_auth_test', email='userA_auth_test@example.com')
        user_a.set_password('passA')
        db.session.add(user_a)
        db.session.commit()
        user_a_id = user_a.id

    # Logar User A e criar a tarefa
    register_user(client, 'userA_auth_test', 'userA_auth_test@example.com', 'passA')
    login_user(client, 'userA_auth_test@example.com', 'passA')

    # Criar a tarefa
    create_task_via_form(client, 'Tarefa do User A', 'Private task', '2025-01-01', 'pendente')

    with app.app_context():
        task_user_a = Task.query.filter_by(title='Tarefa do User A', user_id=user_a_id).first()
        assert task_user_a is not None
        task_id_a = task_user_a.id

    # Deslogar User A
    client.get('/auth/logout', follow_redirects=True)

    # Registrar e Logar User B
    register_user(client, 'userB_auth_test', 'userB_auth_test@example.com', 'passB')
    login_user(client, 'userB_auth_test@example.com', 'passB')

    # Tentar visualizar a tarefa de A
    response_view = client.get(f'/tasks/{task_id_a}')
    assert response_view.status_code == 403

    # Tentar editar a tarefa de A
    response_edit_get = client.get(f'/tasks/{task_id_a}/edit')
    assert response_edit_get.status_code == 403

    response_edit_post = client.post(f'/tasks/{task_id_a}/edit', data={
        'title': 'Tentativa de Edicao',
        'description': 'desc',
        'due_date': '2025-01-01',
        'status': 'pendente'
    })
    assert response_edit_post.status_code == 403

    # Tentar deletar a tarefa de A
    response_delete = client.post(f'/tasks/{task_id_a}/delete')
    assert response_delete.status_code == 403

    # Tentar completar a tarefa de A
    response_complete = client.post(f'/tasks/{task_id_a}/complete')
    assert response_complete.status_code == 403

    # Garantir que a tarefa de A não foi alterada ou excluída
    with app.app_context():
        unchanged_task = db.session.get(Task, task_id_a)
        assert unchanged_task is not None
        assert unchanged_task.title == 'Tarefa do User A'
        assert unchanged_task.user_id == user_a_id
