from dynaconf import Dynaconf
from logging.config import dictConfig

settings = Dynaconf()


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d " "%(thread)d %(message)s"},
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "simple"},
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
        "console_monitoring": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "verbose"}
    },
    "loggers": {
        "default": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "": {"level": "INFO", "handlers": ["console"]},
        "monitoring": {"handlers": ["console_monitoring"], "level": "INFO"}
    },
}


dictConfig(LOGGING)
