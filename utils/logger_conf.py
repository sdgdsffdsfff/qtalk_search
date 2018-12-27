# -*- encoding:utf-8 -*-

import logging
import logging.config


def configure_logger(name, log_path):
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {'format': '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s - %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'},
            'normal': {'format': '%(asctime)s - %(levelname)s - %(message)s',
                        'datefmt': '%Y-%m-%d %H:%M:%S'},

        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'usual': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': log_path,
                'maxBytes': 1024,
                'backupCount': 3
            }
        },
        'loggers': {
            'author': {
                'level': 'DEBUG',
                'handlers': ['console', 'usual']
            },
            'kafka': {
                'level': 'DEBUG',
                'handlers': ['console', 'usual']
            },
            'main': {
                'level': 'DEBUG',
                'handlers': ['console', 'usual']
            },
            'sql': {
                'level': 'DEBUG',
                'handlers': ['console', 'usual']
            }

        },
        'disable_existing_loggers': False
    })
    return logging.getLogger(name)


