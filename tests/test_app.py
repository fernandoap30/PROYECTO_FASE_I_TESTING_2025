import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db, User, Task

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

#inicio del app
def test_home_page(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Entrar' in response.data 

#login de usuarios
def test_login_user(client):
    
    with app.app_context():
        from werkzeug.security import generate_password_hash
        existing_user = User.query.filter_by(username='admin').first()
        if not existing_user:
            user = User(username='admin', password_hash=generate_password_hash('adminpass'))
            db.session.add(user)
            db.session.commit()

    response = client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Agregar Tarea' in response.data or b'<form' in response.data 

#registro de usuario
def test_register_user(client):
    response = client.post('/register', data={
        'username': 'nuevo_usuario',
        'password': 'clave_segura'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Registrarse' in response.data

#crear tarea
def test_create_task(client):
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass'
    }, follow_redirects=True)

    response = client.post('/add', data={
        'title': 'Tarea de prueba',
        'description': 'Descripción de la tarea',
        'priority': 'Alta'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Tarea de prueba' in response.data
    assert 'Descripción de la tarea' in response.get_data(as_text=True)



from werkzeug.security import generate_password_hash

def test_update_task_logic():
    from app import app, Task, db, User

    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        if user is None:
            user = User(username="testuser")
            user.password = generate_password_hash("testpass")
            db.session.add(user)
            db.session.commit()

        task = Task(title='Prueba', description='Desc', priority='Media', user_id=user.id)
        db.session.add(task)
        db.session.commit()

        task.title = 'Actualizado'
        db.session.commit()

        updated_task = db.session.get(Task, task.id)
        assert updated_task.title == 'Actualizado'




@pytest.fixture
def create_task():
    """Fixture para crear una tarea de prueba"""
    with app.app_context(): 
        user = User.query.first()  
        
        if not user:
            user = User(username='testuser', email='test@example.com', password='password')
            db.session.add(user)
            db.session.commit()

        task = Task(title='Tarea de prueba', description='Descripción de la tarea', user_id=user.id)
        db.session.add(task)
        db.session.commit()

        return task

def test_delete_task(create_task):
    """Prueba de eliminación de tarea"""
    with app.app_context():
        task = Task.query.filter_by(title="Tarea de prueba").first()
        assert task is not None
        task_id = task.id

        db.session.delete(task)
        db.session.commit()

        deleted_task = db.session.get(Task, task.id)
        assert deleted_task is None


def test_search_task(client):
    """Prueba de búsqueda de tarea por título o descripción"""

    client.post('/register', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)

    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)

    client.post('/add', data={
        'title': 'Tarea secreta de pruebas',
        'description': 'Contenido no relevante',
        'priority': 'Media'
    }, follow_redirects=True)

    response = client.get('/manage?search=secreta', follow_redirects=True)

    assert b'Tarea secreta de pruebas' in response.data

