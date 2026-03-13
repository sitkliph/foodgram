# Foodgram
Проект Foodgram - сервис кулинарных рецептов. 

![workflow status badge](https://github.com/sitkliph/foodgram/actions/workflows/main.yml/badge.svg)

## Описание проекта:

Foodgram — сайт, на котором пользователи могут публиковать свои рецепты, 
добавлять чужие рецепты в избранное и подписываться на публикации других 
авторов. Зарегистрированным пользователям также доступен сервис 
«Список покупок». Он позволяет создавать список продуктов, которые нужно купить 
для приготовления выбранных блюд.

Просмотр и добавление записей доступны всем аутентифицированным пользователям. 
А редактирование и удаление записей - только авторам и администраторам проекта.

Веб-приложение представляет собой SPA, взаимодействующее с backend-сервисом на 
Django REST Framework.

### Структура проекта:

```
foodgram
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── filters.py
│   │   ├── pagination.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── backends.py
│   │   ├── constants.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── pdf_static/
│   │   ├── fonts/
│   │   │   ├── Raleway-Bold.ttf
│   │   │   └── Raleway-Regular.ttf
│   │   └── logo.png
│   ├── recipes/
│   │   ├── management/
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   └── filldatabase.py
│   │   │   └── __init__.py
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── models.py
│   ├── users/
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── models.py
│   ├── Dockerfile
│   ├── db.sqlite3
│   ├── manage.py
│   └── requirements.txt
├── data/
│   ├── ingredients.csv
│   └── ingredients.json
├── docs/
│   ├── openapi-schema.yml
│   └── redoc.html
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── configs/
│   │   ├── contexts/
│   │   ├── fonts/
│   │   ├── images/
│   │   ├── pages/
│   │   │   ├── about/
│   │   │   ├── cart/
│   │   │   ├── change-password/
│   │   │   ├── favorites/
│   │   │   ├── main/
│   │   │   ├── not-found/
│   │   │   ├── password-reset/
│   │   │   ├── recipe-create/
│   │   │   ├── recipe-edit/
│   │   │   ├── signin/
│   │   │   ├── signup/
│   │   │   ├── single-card/
│   │   │   │   ├── description/
│   │   │   │   ├── ingredients/
│   │   │   │   ├── index.js
│   │   │   │   └── styles.module.css
│   │   │   ├── subscriptions/
│   │   │   ├── technologies/
│   │   │   ├── update-avatar/
│   │   │   ├── user/
│   │   │   └── index.js
│   │   ├── utils/
│   │   │   ├── hex-to-rgba.js
│   │   │   ├── index.js
│   │   │   ├── use-recipe.js
│   │   │   ├── use-recipes.js
│   │   │   ├── use-subscriptions.js
│   │   │   ├── use-tags.js
│   │   │   └── validation.js
│   │   ├── App.css
│   │   ├── App.js
│   │   ├── App.test.js
│   │   ├── index.css
│   │   ├── index.js
│   │   ├── logo.svg
│   │   ├── reportWebVitals.js
│   │   ├── setupTests.js
│   │   └── styles.module.css
│   ├── Dockerfile
│   ├── package-lock.json
│   ├── package.json
│   └── yarn.lock
├── infra/
│   ├── Dockerfile
│   ├── docker-compose.production.yml
│   ├── docker-compose.yml
│   └── nginx.conf
├── postman_collection/
│   ├── README.md
│   ├── clear_db.sh
│   └── foodgram.postman_collection.json
├── LICENSE
├── README.md
└── setup.cfg
```

### Стек использованных технологий:

- Python 3.12.7
- Django 6.0.2
- Django REST Framework 3.16.1
- Gunicorn 25.1.0
- ReportLab 4.4.10
- SQLite
- PostgreSQL
- React
- Docker

## Установка и запуск проекта:

### 1. Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/sitkliph/foodgram
```

```bash
cd foodgram
```

### 2. Установить и запустить Docker.

### 3. Создать файл `.env` и заполнить по примеру файла `.env.example`

### 4. Запустить Docker Compose:

```bash
docker compose up -d
```

### 5. Выполнить миграции, заполнить данные и собрать статику backend-приложения:

```bash
docker compose exec backend bash
python manage.py migrate
python manage.py filldatabase
python manage.py collectstatic
exit
```

## Автор
### Бакин Сергей
e-mail: sergey.bakin2000@gmail.com