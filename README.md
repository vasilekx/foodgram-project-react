# Продуктовый помощник

## Описание

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Применяемые технологии
[![Python](https://img.shields.io/badge/Python-3.7-blue?style=flat-square&logo=Python&logoColor=3776AB&labelColor=d0d0d0)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-2.2.16-blue?style=flat-square&logo=Django&logoColor=092E20&labelColor=d0d0d0)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/Django%20REST%20Framework-3.12.4-blue?style=flat-square&logo=Django&logoColor=a30000&labelColor=d0d0d0)](https://www.django-rest-framework.org/)
[![Simple JWT](https://img.shields.io/badge/Simple%20JWT%20-4.7.2-blue?style=flat-square&logo=github&logoColor=4285F4&labelColor=d0d0d0)](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
[![gunicorn](https://img.shields.io/badge/gunicorn-20.0.4-blue?style=flat-square&logo=gunicorn&logoColor=499848&labelColor=d0d0d0)](https://gunicorn.org/)
[![Postgres](https://img.shields.io/badge/Postgres-13.0-blue?style=flat-square&logo=PostgreSQL&logoColor=4169E1&labelColor=d0d0d0)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/Nginx-1.21.3-blue?style=flat-square&logo=NGINX&logoColor=009639&labelColor=d0d0d0)](https://nginx.org/ru/)
[![Docker](https://img.shields.io/badge/Docker-20.10.16-blue?style=flat-square&logo=Docker&logoColor=2496ED&labelColor=d0d0d0)](https://www.docker.com/)
[![Docker-Compose](https://img.shields.io/badge/Docker%20Compose-2.5.0-blue?style=flat-square&logo=Docker&logoColor=2496ED&labelColor=d0d0d0)](https://www.docker.com/)

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-service-blue?style=flat-square&logo=Docker&logoColor=2496ED&labelColor=d0d0d0)](https://hub.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/GitHub%20Actions-service-blue?style=flat-square&logo=GitHub%20actions&logoColor=2088FF&labelColor=d0d0d0)](https://github.com/features/actions/)
[![Yandex.Cloud](https://img.shields.io/badge/Yandex.Cloud-service-blue?style=flat-square&labelColor=d0d0d0)](https://cloud.yandex.ru/)

## Установка сервиса
Проверьте установлен ли у вас Docker 
```bash
sudo docker -v
```
Если Docker отсутствует, то необходимо его [установить](https://docs.docker.com/engine/install/). Вместе с Docker также устанавливается Docker Compose. После установки, проверьте установлена ли у вас Docker Compose версии 2.5.0 или новее:
```bash
sudo docker-compose -v
```
Если версия Docker Compose ниже 2.5.0 необходимо [обновить Docker Compose](https://docs.docker.com/compose/install/).


Клонировать репозиторий:
```bash
git clone git@github.com:vasilekx/foodgram-project-react.git
```
Перейти в папку infra 
```bash
cd infra
```
Cоздать в директории файл .env со следующими параметрами:
```python
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
POSTGRES_DB=postgres_db_1 # имя базы данных
POSTGRES_USER=postgres_user_1 # логин для подключения к базе данных
POSTGRES_PASSWORD=qawsed123456 # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
DJANGO_SECRET_KEY='DJANGO_SECRET_KEY' # секретный ключ Django
DJANGO_ALLOWED_HOSTS='web localhost 127.0.0.1 [::1]' # cписок хостов/доменов, для которым доступен проект
```
Создать и запустить контейнеры: 
```bash
sudo docker-compose up -d
```
[***Обзор команд*** ](https://docs.docker.com/compose/reference/)*для работы с docker-compose.*

Выполнить миграции:
```bash
sudo docker-compose exec web python manage.py migrate
```
Создать суперпользователя:
```bash
sudo docker-compose exec web python manage.py createsuperuser
```
Собирать статические файлы:
```bash
sudo docker-compose exec web python manage.py collectstatic --no-input
```
Заполнить базу данными(теги, пользователи и ингредиенты):
```bash
sudo docker-compose exec web python manage.py load_initial_data
```

## Документация к API продуктового помощника
```
http://x.x.x.x/x/
```
## Административная панель
```
http://x.x.x.x/admin/
```

## Авторы
1. Владислав Василенко ([vasilekx](https://github.com/vasilekx))
