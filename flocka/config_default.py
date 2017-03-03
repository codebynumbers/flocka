DEBUG = True
ASSETS_DEBUG = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

SECRET_KEY = 'secret key'

CACHE_TYPE = 'null'
CACHE_NO_NULL_WARNING = True

SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/flocka.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
#SQLALCHEMY_DATABASE_URI = 'mysql://flocka:flocka@localhost:3306/flocka?charset=utf8'

NGINX_SITES_PATH = '/etc/nginx/sites-enabled'
NGINX_RELOAD_CMD = 'sudo service nginx reload'
