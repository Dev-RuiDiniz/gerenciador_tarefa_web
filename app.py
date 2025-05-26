from flask import Flask, render_template
from flask_login import LoginManager, current_user
from config import Config
from extensions import db  # db importado daqui
from models import User, Task
from auth import auth_bp
from forms import RegistrationForm, LoginForm

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)  # Inicializa db com app

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def home():
    return render_template('index.html', title='Início', current_user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
