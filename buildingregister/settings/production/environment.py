import django_heroku
from split_settings.tools import include

include(
    "../common/*.py",
    "security.py",
)

django_heroku.settings(locals())
