LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
        },
    },
    'formatters': {
        'brief': {
            'format': '%(levelname)s %(name)s %(message)s',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'buildingregister': {'level': 'INFO'},
        'register': {'level': 'INFO'},
        'django': {'level': 'INFO'},
    },
}
from logging.config import dictConfig
dictConfig(LOGGING)