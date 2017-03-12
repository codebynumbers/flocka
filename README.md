# Flocka

Flask + Docker = a little flock of application branches

#### Getting Started, assumes fully-stocked virtualenv

`make rename somnewapp=somenewapp`

Alembic initialize

`./manage.py db init`

Edit migrations/alembic.ini - a good file_template is:

`%%(year)d-%%(month).2d-%%(day).2d_%%(hour).2d-%%(minute).2d-%%(second).2d_%%(rev)s_%%(slug)s`

Create initial migrations

`./manage.py db migrate`

Apply to database

`./manage.py db upgrade`

Start

`./manage.py runserver`

Original Documentation is located at [https://jackstouffer.github.io/Flask-Foundation/](https://jackstouffer.github.io/Flask-Foundation/)

