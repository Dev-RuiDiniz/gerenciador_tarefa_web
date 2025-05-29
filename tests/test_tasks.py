# tests/test_tasks.py
import pytest
from extensions import db
from models import User, Task
from datetime import datetime

# Importa as funções auxiliares de auth para login
from tests.test_auth import register_user, login_user

@pytest.fixture
def logged_in_user(client):
    """Fixture para registrar e logar um usuário para testes de tarefa."""
    register_user(client, 'taskuser', 'task@example.com', 'taskpass')
    login_user(client, 'task@example.com', 'taskpass')
    with client.application.app_context():
        user = User.query.filter_by(username='taskuser').first()
        return user # Retorna o objeto User logado

def create_task_via_form(client, title, description, due_date, status):
    """Função auxiliar para criar uma tarefa via formulário."""
    return client.post('/tasks/new', data={
        'title': title,
        'description': description,
        'due_date': due_date, # Formato YYYY-MM-DD
        'status': status
    }, follow_redirects=True)

def test_list_tasks_page_loads(client, logged_in_user):
    """Testa se a página de listagem de tarefas carrega para um usuário logado."""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert b"Minhas Tarefas" in response.data

def test_create_task_success(client, logged_in_user):
    """Testa a criação bem-sucedida de uma tarefa."""
    response = create_task_via_form(client, 'Tarefa de Teste', 'Descricao da tarefa', '2025-12-31', 'pendente')
    assert b"Tarefa criada com sucesso!" in response.data
    assert b"Minhas Tarefas" in response.data # Redireciona para a lista

    with client.application.app_context():
        task = Task.query.filter_by(title='Tarefa de Teste').first()
        assert task is not None
        assert task.description == 'Descricao da tarefa'
        assert task.status == 'pendente'
        assert task.author.id == logged_in_user.id # Verifica se a tarefa foi associada ao usuário correto

def test_view_task_details(client, logged_in_user):
    """Testa a visualização dos detalhes de uma tarefa."""
    # Criar uma tarefa diretamente no banco de dados para o teste
    with client.application.app_context():
        new_task = Task(title='Ver Detalhes', description='Detalhes importantes',
                        due_date=datetime(2025, 11, 15).date(), status='pendente', author=logged_in_user)
        db.session.add(new_task)
        db.session.commit()
        task_id = new_task.id

    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    assert b"Ver Detalhes" in response.data
    assert b"Detalhes importantes" in response.data

def test_view_non_existent_task(client, logged_in_user):
    """Testa a visualização de uma tarefa inexistente."""
    response = client.get('/tasks/99999') # ID que provavelmente não existe
    assert response.status_code == 404 # Espera um erro 404

def test_edit_task_success(client, logged_in_user):
    """Testa a edição bem-sucedida de uma tarefa."""
    with client.application.app_context():
        task_to_edit = Task(title='Tarefa Antiga', description='Desc. Antiga',
                            due_date=datetime(2025, 1, 1).date(), status='pendente', author=logged_in_user)
        db.session.add(task_to_edit)
        db.session.commit()
        task_id = task_to_edit.id

    response = client.post(f'/tasks/{task_id}/edit', data={
        'title': 'Tarefa Nova',
        'description': 'Desc. Nova',
        'due_date': '2025-02-01',
        'status': 'concluida'
    }, follow_redirects=True)

    assert b"Tarefa atualizada com sucesso!" in response.data
    assert b"Tarefa Nova" in response.data # Redireciona para a visualização da tarefa

    with client.application.app_context():
        updated_task = Task.query.get(task_id)
        assert updated_task.title == 'Tarefa Nova'
        assert updated_task.description == 'Desc. Nova'
        assert updated_task.status == 'concluida'
        assert updated_task.due_date == datetime(2025, 2, 1).date()

def test_delete_task_success(client, logged_in_user):
    """Testa a exclusão bem-sucedida de uma tarefa."""
    with client.application.app_context():
        task_to_delete = Task(title='Tarefa para Deletar', description='Delete-me',
                              due_date=datetime(2025, 3, 3).date(), status='pendente', author=logged_in_user)
        db.session.add(task_to_delete)
        db.session.commit()
        task_id = task_to_delete.id

    response = client.post(f'/tasks/{task_id}/delete', follow_redirects=True)
    assert b"Tarefa exclu\xc3\xadda com sucesso!" in response.data
    assert b"Minhas Tarefas" in response.data

    with client.application.app_context():
        assert Task.query.get(task_id) is None # Verifica se a tarefa foi removida

def test_complete_task_success(client, logged_in_user):
    """Testa a marcação de uma tarefa como concluída."""
    with client.application.app_context():
        task_to_complete = Task(title='Tarefa Incompleta', description='Completar agora',
                                due_date=datetime(2025, 4, 4).date(), status='pendente', author=logged_in_user)
        db.session.add(task_to_complete)
        db.session.commit()
        task_id = task_to_complete.id

    response = client.post(f'/tasks/{task_id}/complete', follow_redirects=True)
    assert b"Tarefa marcada como conclu\xc3\xadda!" in response.data
    assert b"Minhas Tarefas" in response.data

    with client.application.app_context():
        completed_task = Task.query.get(task_id)
        assert completed_task.status == 'concluida'

def test_uncomplete_task_success(client, logged_in_user):
    """Testa a marcação de uma tarefa como pendente novamente."""
    with client.application.app_context():
        task_to_uncomplete = Task(title='Tarefa Completa', description='Reverter',
                                  due_date=datetime(2025, 5, 5).date(), status='concluida', author=logged_in_user)
        db.session.add(task_to_uncomplete)
        db.session.commit()
        task_id = task_to_uncomplete.id

    response = client.post(f'/tasks/{task_id}/uncomplete', follow_redirects=True)
    assert b"Tarefa marcada como pendente novamente!" in response.data
    assert b"Minhas Tarefas" in response.data

    with client.application.app_context():
        uncompleted_task = Task.query.get(task_id)
        assert uncompleted_task.status == 'pendente'

def test_task_authorization(client):
    """Testa que um usuário não pode acessar/modificar tarefas de outro usuário."""
    # Usuário A
    register_user(client, 'userA', 'userA@example.com', 'passA')
    login_user(client, 'userA@example.com', 'passA')
    with client.application.app_context():
        user_a = User.query.filter_by(username='userA').first()
        task_user_a = Task(title='Tarefa do User A', description='Private', author=user_a)
        db.session.add(task_user_a)
        db.session.commit()
        task_id_a = task_user_a.id

    # Usuário B tenta acessar a tarefa de A
    logout_user(client) # Desloga User A
    register_user(client, 'userB', 'userB@example.com', 'passB')
    login_user(client, 'userB@example.com', 'passB')

    # Tentar visualizar
    response_view = client.get(f'/tasks/{task_id_a}')
    assert response_view.status_code == 403 # Forbidden

    # Tentar editar
    response_edit = client.post(f'/tasks/{task_id_a}/edit', data={
        'title': 'Tentativa de Edicao', 'description': '', 'due_date': '', 'status': 'pendente'
    })
    assert response_edit.status_code == 403 # Forbidden

    # Tentar deletar
    response_delete = client.post(f'/tasks/{task_id_a}/delete')
    assert response_delete.status_code == 403 # Forbidden

    # Tentar completar
    response_complete = client.post(f'/tasks/{task_id_a}/complete')
    assert response_complete.status_code == 403 # Forbidden

    # Verificar que a tarefa de A não foi alterada
    with client.application.app_context():
        assert Task.query.get(task_id_a).title == 'Tarefa do User A'