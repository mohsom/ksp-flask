# Flask Tasks

Маленький список задач на Flask: додавання, позначення виконаним, видалення, плюс JSON-ендпоінт `/api/tasks`.

## Швидкий старт

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask --app run run --debug -p 5001   # або: python run.py (порт 5000)
```

> На macOS порт 5000 часто зайнятий AirPlay Receiver (відповідає 403) — використовуйте інший порт.

Тести: `pytest`

## Стек

Flask · Flask-SQLAlchemy (SQLAlchemy 2) · Flask-WTF (форми + CSRF) · Jinja2 · SQLite

## Структура

```
ksp-flask/
├── run.py              # точка входу: app = create_app()
├── config.py           # Config / TestConfig (клас-конфіги, змінні оточення)
├── app/
│   ├── __init__.py     # application factory create_app()
│   ├── extensions.py   # db, csrf — створені без app, ініціалізуються у фабриці
│   ├── models.py       # Task
│   ├── forms.py        # TaskForm (WTForms)
│   ├── routes.py       # Blueprint "tasks": маршрути й логіка
│   └── templates/index.html
└── tests/test_app.py   # pytest, in-memory SQLite
```

Ключові ідеї:

- **Application factory** — `create_app(config)` створює окремий екземпляр застосунку. Це дозволяє мати різні конфіги (dev/test) і не тримати глобального стану.
- **Extensions без app** — `db = SQLAlchemy()` оголошено окремо й підключається через `db.init_app(app)`, щоб уникнути циклічних імпортів.
- **Blueprint** — спосіб групувати маршрути в модулі (аналог застосунку в Django).
- **Application / request context** — `current_app`, `g`, `request`, `session` доступні лише в контексті; саме тому `db.create_all()` виконується в `app.app_context()`.

## Маршрути

| Метод | URL | Дія |
|-------|-----|-----|
| GET, POST | `/` | список задач / додати задачу |
| POST | `/tasks/<id>/toggle` | змінити статус |
| POST | `/tasks/<id>/delete` | видалити |
| GET | `/api/tasks` | JSON зі списком |

## Життєвий цикл запиту у Flask

```
Браузер → WSGI-сервер (Werkzeug / gunicorn)
        → Flask app: before_request-хуки
        → URL map (Werkzeug routing) → view-функція
        → db (SQLAlchemy session) / render_template (Jinja2)
        → after_request-хуки → Response → Браузер
```

## Flask vs Django

| | **Flask** | **Django** |
|---|---|---|
| Філософія | Мікрофреймворк: мінімальне ядро, решту обираєш сам | «Batteries included»: усе потрібне з коробки |
| Ядро | Werkzeug (WSGI, роутинг) + Jinja2 | Власний стек: ORM, шаблони, форми, адмінка, auth |
| Структура проєкту | Довільна, вирішуєш сам (factory, blueprints) | Жорстка конвенція: project + apps, `settings.py`, `urls.py` |
| ORM / БД | Немає в ядрі; зазвичай SQLAlchemy (патерн Data Mapper, дуже гнучкий) | Власний ORM (Active Record), тісно інтегрований із моделями |
| Міграції | Окремо: Alembic / Flask-Migrate | Вбудовані (`makemigrations`, `migrate`) |
| Адмінка | Немає (Flask-Admin як сторонній пакет) | Автогенерована адмінка з коробки |
| Автентифікація | Flask-Login / Flask-Security | Вбудована (`User`, права, групи, сесії) |
| Форми й CSRF | Flask-WTF | Вбудовані `forms`, `ModelForm`, CSRF middleware |
| Шаблони | Jinja2 (потужніший синтаксис, виклики функцій) | DTL (простіший, більш обмежений) |
| Роутинг | Декоратори `@app.route` біля в’ю | Централізований `urls.py` (URLconf) |
| Конфігурація | Об’єкт/словник `app.config`, довільно | `settings.py` з готовими розділами |
| Контекст | `request`, `g`, `session` — глобальні проксі через контексти | `request` передається явно в кожне в’ю |
| API | Просто `jsonify`; REST через Flask-RESTful / apiflask | Django REST Framework (де-факто стандарт) |
| Тести | Test client, pytest (будь-що) | `TestCase`, test client, тестова БД «з коробки» |
| Крива навчання | Низький старт, але багато рішень на розробнику | Вищий старт, зате чіткий шлях |
| Коли обирати | Мікросервіси, невеликі API, прототипи, нестандартна архітектура | Великі контентні/CRUD-системи, швидкий старт із адмінкою й auth |

**Коротко:** Flask дає свободу та мінімум, але вимагає самому підбирати й інтегрувати бібліотеки; Django дає готову, узгоджену платформу та конвенції ціною меншої гнучкості. Обидва працюють поверх WSGI (Django ще й ASGI; Flask — частково через async-в’ю).

### Той самий функціонал у двох фреймворках

| Задача | Flask (цей проєкт) | Django ([ksp-django](https://github.com/mohsom/ksp-django)) |
|---|---|---|
| Створити застосунок | `create_app()` | `django-admin startproject` + `startapp` |
| Модель | `class Task(db.Model)` | `class Post(models.Model)` |
| Схема БД | `db.create_all()` (або Alembic) | `makemigrations` + `migrate` |
| Маршрут | `@bp.route('/')` | `path('', views.post_list)` у `urls.py` |
| Запит до БД | `db.select(Task)`, `db.get_or_404` | `Post.objects.filter(...)`, `get_object_or_404` |
| Шаблон | `render_template('index.html', ...)` | `render(request, 'blog/post_list.html', ...)` |
| Форма | `FlaskForm` + `validate_on_submit()` | `ModelForm` + `is_valid()` |
| CSRF | `CSRFProtect` + `csrf_token()` | middleware + `{% csrf_token %}` |
| Захист доступу | Flask-Login `@login_required` | `@login_required` з коробки |
