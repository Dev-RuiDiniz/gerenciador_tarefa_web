# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms.fields import DateField # Para a data de vencimento (due_date)
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Usuário',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Esse nome de usuário já está em uso. Por favor, escolha outro.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Esse email já está registrado. Por favor, use outro ou faça login.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Senha',
                             validators=[DataRequired()])
    submit = SubmitField('Login')

class TaskForm(FlaskForm):
    title = StringField('Título da Tarefa',
                        validators=[DataRequired(), Length(min=5, max=100)])
    description = TextAreaField('Descrição',
                                validators=[Optional(), Length(max=500)]) # Optional para permitir vazio
    due_date = DateField('Prazo (YYYY-MM-DD)', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Status',
                         choices=[('pendente', 'Pendente'), ('concluida', 'Concluída')],
                         validators=[DataRequired()])
    submit = SubmitField('Salvar Tarefa')