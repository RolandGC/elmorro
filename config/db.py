import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _env(name, default=None):
    return os.environ.get(name, default)


SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': _env('SQLITE_NAME', os.path.join(BASE_DIR, 'db', 'elmorro.sqlite3')),
    }
}

# PostgreSQL (driver: psycopg2-binary). Configurar via variables de entorno.
POSTGRESQL = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _env('DB_NAME', 'elmorro'),
        'USER': _env('DB_USER', 'elmorro'),
        'PASSWORD': _env('DB_PASSWORD', ''),
        'HOST': _env('DB_HOST', '127.0.0.1'),
        'PORT': _env('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(_env('DB_CONN_MAX_AGE', '60')),
        'ATOMIC_REQUESTS': True,
        'OPTIONS': {
            'connect_timeout': int(_env('DB_CONNECT_TIMEOUT', '10')),
        },
    }
}

# mysqlclient

MYSQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': _env('MYSQL_NAME', 'elmorro'),
        'USER': _env('MYSQL_USER', 'root'),
        'PASSWORD': _env('MYSQL_PASSWORD', ''),
        'HOST': _env('MYSQL_HOST', 'localhost'),
        'PORT': _env('MYSQL_PORT', ''),
    }
}

# django-mssql-backend (django 3.0.6)

SQLSERVER = {
    'default': {
        'ENGINE': 'sql_server.pyodbc',
        'NAME': _env('MSSQL_NAME', 'elmorro'),
        'USER': _env('MSSQL_USER', ''),
        'PASSWORD': _env('MSSQL_PASSWORD', ''),
        'HOST': _env('MSSQL_HOST', 'localhost'),
        'PORT': _env('MSSQL_PORT', '1433'),
        'OPTIONS': {
            'driver': 'SQL Server Native Client 10.0',
        },
    }
}

# Selector de motor. Por defecto PostgreSQL.
# Para volver a SQLite temporalmente: export DB_ENGINE=sqlite
_ENGINE = _env('DB_ENGINE', 'postgresql').lower()

if _ENGINE == 'sqlite':
    DATABASES = SQLITE
elif _ENGINE == 'mysql':
    DATABASES = MYSQL
elif _ENGINE == 'sqlserver':
    DATABASES = SQLSERVER
else:
    DATABASES = POSTGRESQL
