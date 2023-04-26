# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
import dj_database_url

MAX_CONN_AGE = 600

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR}/db.sqlite3",
        conn_max_age=MAX_CONN_AGE,
        ssl_require=False,
    ),
}
