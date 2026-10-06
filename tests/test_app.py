import pytest

from app import create_app
from app.extensions import db
from app.models import Task
from config import TestConfig


@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as c:
        yield c
    with app.app_context():
        db.drop_all()


def test_empty_index(client):
    assert 'Задач поки немає' in client.get('/').get_data(as_text=True)


def test_add_toggle_delete(client):
    client.post('/', data={'title': 'Learn Flask'})
    assert client.get('/api/tasks').get_json() == [{'id': 1, 'title': 'Learn Flask', 'done': False}]
    client.post('/tasks/1/toggle')
    assert client.get('/api/tasks').get_json()[0]['done'] is True
    client.post('/tasks/1/delete')
    assert client.get('/api/tasks').get_json() == []


def test_validation_rejects_empty_title(client):
    r = client.post('/', data={'title': ''})
    assert r.status_code == 200
    assert client.get('/api/tasks').get_json() == []


def test_404(client):
    assert client.post('/tasks/42/toggle').status_code == 404
