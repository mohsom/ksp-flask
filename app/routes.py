from flask import Blueprint, jsonify, redirect, render_template, url_for

from .extensions import db
from .forms import TaskForm
from .models import Task

bp = Blueprint('tasks', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = TaskForm()
    if form.validate_on_submit():
        db.session.add(Task(title=form.title.data))
        db.session.commit()
        return redirect(url_for('tasks.index'))
    tasks = db.session.scalars(db.select(Task).order_by(Task.created_at)).all()
    return render_template('index.html', tasks=tasks, form=form)


@bp.post('/tasks/<int:task_id>/toggle')
def toggle(task_id):
    task = db.get_or_404(Task, task_id)
    task.done = not task.done
    db.session.commit()
    return redirect(url_for('tasks.index'))


@bp.post('/tasks/<int:task_id>/delete')
def delete(task_id):
    db.session.delete(db.get_or_404(Task, task_id))
    db.session.commit()
    return redirect(url_for('tasks.index'))


@bp.get('/api/tasks')
def api_tasks():
    tasks = db.session.scalars(db.select(Task).order_by(Task.created_at)).all()
    return jsonify([t.to_dict() for t in tasks])
