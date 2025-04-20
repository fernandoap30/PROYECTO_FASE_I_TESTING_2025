from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'tu_clave_secreta'

# Inicializa la base de datos
db = SQLAlchemy(app)

# Define el modelo de Task (Tarea)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=db.func.now())

# Ruta principal (mostrar todas las tareas)
@app.route('/')
def index():
    tasks = Task.query.all()  # Obtiene todas las tareas
    return render_template('index.html', tasks=tasks)

# Ruta para agregar una tarea
@app.route('/add', methods=['POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        priority = request.form['priority']

        new_task = Task(title=title, description=description, priority=priority)
        try:
            db.session.add(new_task)
            db.session.commit()
            flash('Tarea agregada exitosamente', 'success')
        except:
            db.session.rollback()
            flash('Error al agregar la tarea', 'error')

    return redirect(url_for('index'))

# Ruta para eliminar una tarea
@app.route('/delete/<int:id>')
def delete_task(id):
    task = Task.query.get(id)
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Tarea eliminada exitosamente', 'success')
    except:
        db.session.rollback()
        flash('Error al eliminar la tarea', 'error')
    
    return redirect(url_for('index'))

@app.route('/modify')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
    app.run(debug=True)
