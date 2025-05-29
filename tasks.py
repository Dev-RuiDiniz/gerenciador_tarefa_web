# tasks.py
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from extensions import db # Importa a instância do SQLAlchemy
from models import Task # Importa o modelo Task
from forms import TaskForm # Importa o formulário de tarefa

tasks_bp = Blueprint('tasks', __name__, template_folder='templates', static_folder='static')

@tasks_bp.route('/tasks')
@login_required # Garante que apenas usuários logados possam ver as tarefas
def list_tasks():
    # Filtra as tarefas pelo usuário logado
    tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()
    # Adicionando funcionalidade de filtro por status
    status_filter = request.args.get('status')
    if status_filter in ['pendente', 'concluida']:
        tasks = Task.query.filter_by(user_id=current_user.id, status=status_filter).order_by(Task.created_at.desc()).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()

    return render_template('list_tasks.html', title='Minhas Tarefas', tasks=tasks, status_filter=status_filter)

@tasks_bp.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status=form.status.data,
            author=current_user # Associa a tarefa ao usuário logado
        )
        db.session.add(task)
        db.session.commit()
        flash('Tarefa criada com sucesso!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    return render_template('create_task.html', title='Nova Tarefa', form=form)

@tasks_bp.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    # Garante que o usuário só possa ver suas próprias tarefas
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403) # Proíbe acesso se a tarefa não pertence ao usuário
    return render_template('view_task.html', title=task.title, task=task)

@tasks_bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)

    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        db.session.commit()
        flash('Tarefa atualizada com sucesso!', 'success')
        return redirect(url_for('tasks.view_task', task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.due_date.data = task.due_date # Preenche o campo de data
        form.status.data = task.status # Preenche o status atual
    return render_template('edit_task.html', title='Editar Tarefa', form=form, task=task)

@tasks_bp.route('/tasks/<int:task_id>/delete', methods=['POST']) # Usamos POST para exclusão por segurança
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Tarefa excluída com sucesso!', 'info')
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/tasks/<int:task_id>/complete', methods=['POST']) # Rota específica para marcar como concluída
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    task.status = 'concluida'
    db.session.commit()
    flash('Tarefa marcada como concluída!', 'success')
    return redirect(url_for('tasks.list_tasks'))

@tasks_bp.route('/tasks/<int:task_id>/uncomplete', methods=['POST']) # Opcional: para reverter para pendente
@login_required
def uncomplete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    task.status = 'pendente'
    db.session.commit()
    flash('Tarefa marcada como pendente novamente!', 'info')
    return redirect(url_for('tasks.list_tasks'))