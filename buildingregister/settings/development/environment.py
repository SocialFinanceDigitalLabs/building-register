from split_settings.tools import include, optional

DEBUG = True

include(
    "../common/*.py",
    "database.py",
    "security.py",
)
