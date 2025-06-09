import os

LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": LOG_FILE_PATH,
            "mode": "a",
        },
    },

    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    },
}
