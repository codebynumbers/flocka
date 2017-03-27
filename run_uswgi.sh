#!/bin/sh
uwsgi --http localhost:5000 --processes=4 --master --single-interpreter --die-on-term --env LC_ALL='en_US.UTF-8' --env LANG='en_US.UTF-8' -w wsgi_app:app
