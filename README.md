# Gerenciador de Tarefas Web

Este é um aplicativo web simples de gerenciamento de tarefas construído com **Flask**, oferecendo funcionalidades de autenticação de usuário e operações CRUD (Criar, Ler, Atualizar, Excluir) para tarefas. A interface é responsiva, com um design moderno em tons de cinza e azul, e inclui testes unitários robustos usando Pytest.

---

## Funcionalidades Principais

### 🔐 Autenticação e Autorização

O sistema de autenticação é robusto e seguro, gerenciando o acesso de usuários e protegendo as rotas.

* **Registro de Usuários:** Crie novas contas de usuário através da rota `/auth/register`. Senhas são armazenadas de forma segura usando *hashing*.
* **Login de Usuários:** Autentique-se com seu email e senha na rota `/auth/login` para acessar as funcionalidades do sistema.
* **Logout:** Encerre sua sessão a qualquer momento através da rota `/auth/logout`.
* **Proteção de Rotas:** Utiliza o **Flask-Login** para garantir que apenas usuários autenticados possam acessar e manipular suas tarefas. Rotas protegidas automaticamente redirecionam para a página de login se o usuário não estiver autenticado.

### ✅ CRUD de Tarefas

Cada usuário tem sua própria lista de tarefas, que pode ser gerenciada através das seguintes operações:

* **Criar Tarefa:** Adicione novas tarefas com título, descrição opcional, prazo e status inicial (`pendente`). A rota `/tasks/new` (ou simplesmente `/new` após o login) exibe o formulário e processa o envio.
* **Listar Tarefas:** Visualize todas as suas tarefas na rota `/tasks`. As tarefas são listadas em ordem decrescente de criação e podem ser filtradas por status (`pendente` ou `concluída`).
* **Ver Detalhes da Tarefa:** Acesse informações completas de uma tarefa específica na rota `/tasks/<int:task_id>`.
* **Atualizar Tarefa:** Modifique o título, descrição, prazo ou status de uma tarefa existente através da rota `/tasks/<int:task_id>/edit`.
* **Excluir Tarefa:** Remova uma tarefa permanentemente na rota `/tasks/<int:task_id>/delete`. Há uma confirmação via JavaScript antes da exclusão.
* **Marcar como Concluída/Pendente:** Altere rapidamente o status de uma tarefa para `concluída` ou volte para `pendente` através de botões dedicados na listagem ou na visualização de detalhes.

---

## Estrutura do Projeto

* `app.py`: O arquivo principal da aplicação Flask, onde o aplicativo, o banco de dados e o gerenciador de login são inicializados, e os Blueprints são registrados.
* `config.py`: Contém as configurações da aplicação, como a chave secreta e a URI do banco de dados.
* `models.py`: Define os modelos de banco de dados para `User` e `Task` usando SQLAlchemy.
* `forms.py`: Contém as classes de formulário para registro, login e tarefas, utilizando Flask-WTF para validação.
* `auth.py`: Um Blueprint para todas as rotas relacionadas à autenticação (registro, login, logout).
* `tasks.py`: Um Blueprint para todas as rotas de gerenciamento de tarefas (CRUD).
* `static/`: Contém arquivos estáticos.
    * `css/style.css`: Estilos CSS responsivos com um tema moderno em tons de cinza e azul.
    * `js/main.js`: Lógica JavaScript básica para interatividade (ex: confirmação de exclusão, mensagens flash que desaparecem).
* `templates/`: Contém os arquivos HTML (Jinja2) para todas as páginas da aplicação.
    * `base.html`: O template base que inclui cabeçalho, rodapé, navegação e mensagens flash.
    * `index.html`: A página inicial do aplicativo.
    * `login.html`, `register.html`: Páginas para autenticação de usuário.
    * `list_tasks.html`, `create_task.html`, `view_task.html`, `edit_task.html`: Páginas para o gerenciamento de tarefas.
* `tests/`: Contém os testes unitários da aplicação.
    * `conftest.py`: Fixtures e configurações globais para o Pytest, incluindo a configuração de um banco de dados SQLite em memória para testes isolados.
    * `test_auth.py`: Testes unitários para as funcionalidades de registro, login e logout.
    * `test_tasks.py`: Testes unitários para as operações de CRUD de tarefas e autorização.

---

## Como Rodar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone <url_do_seu_repositorio>
    cd gerenciador_tarefa_web
    ```
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Execute a aplicação:**
    ```bash
    python app.py
    ```
    O aplicativo estará disponível em `http://127.0.0.1:5000/`.

---

## Como Rodar os Testes

1.  **Certifique-se de estar no diretório raiz do projeto** (onde está `app.py`).
2.  **Execute o Pytest:**
    ```bash
    pytest
    ```
    Isso executará todos os testes unitários configurados em `tests/`.

---

## Próximos Passos (Sugestões de Melhorias)

* **Validação de Formulário Front-end:** Adicionar validação JavaScript aos formulários para uma melhor experiência do usuário.
* **Paginação:** Implementar paginação na listagem de tarefas para lidar com um grande volume de dados.
* **Funcionalidades de Pesquisa:** Adicionar uma barra de pesquisa para filtrar tarefas por título ou descrição.
* **Notificações:** Adicionar um sistema de notificação para prazos de tarefas.
* **Dockerização:** Configurar Docker para facilitar a implantação e o gerenciamento de dependências.
* **Implantação:** Preparar a aplicação para implantação em um servidor de produção (ex: Heroku, AWS, DigitalOcean).

---

Sinta-se à vontade para explorar, modificar e expandir este projeto!