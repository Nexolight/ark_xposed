import os
import sys
spath = os.path.dirname(sys.argv[0])
_FORMATERS = {
    'detailed': {
        'format':'%(asctime)s %(levelname)-8s %(name)-45s %(message)s'
    },
    'simple': {
        'format':'%(levelname)-8s %(name)-45s %(message)s'
    },
}

_HANDLERS = {
    'console': {
        'class': 'logging.StreamHandler',
        'level': 'DEBUG',
        'formatter': 'simple',
        'stream': 'ext://sys.stdout',
    },
    'xposed_file': {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'DEBUG',
        'formatter': 'detailed',
        'filename': os.path.join(spath,'logs/xposed.log'),
        'mode': 'a',
        'maxBytes': 10485760,
        'backupCount': 3,
    },
    'ark_chatlog_file': {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'DEBUG',
        'formatter': 'detailed',
        'filename': os.path.join(spath,'logs/chatlog.log'),
        'mode': 'a',
        'maxBytes': 10485760,
        'backupCount': 3,
    },
    'ark_statistics_file': {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 'DEBUG',
        'formatter': 'detailed',
        'filename': os.path.join(spath,'logs/statistics.log'),
        'mode': 'a',
        'maxBytes': 10485760,
        'backupCount': 3,
    },
}

XPOSED_LOG={
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': _HANDLERS,
	'formatters':_FORMATERS,
	'loggers': {
		'': {
			'level':'DEBUG',
			'handlers':['xposed_file','console']
		}
	}
}

CHATLOG_LOG={
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': _HANDLERS,
	'formatters':_FORMATERS,
	'loggers': {
		'': {
			'level':'DEBUG',
			'handlers':['ark_chatlog_file','console']
		}
	}
}

STATISTICS_LOG={
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': _HANDLERS,
	'formatters':_FORMATERS,
	'loggers': {
		'': {
			'level':'DEBUG',
			'handlers':['ark_statistics_file','console']
		}
	}
}

CHATLOG_LOG={
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': _HANDLERS,
	'formatters':_FORMATERS,
	'loggers': {
		'': {
			'level':'DEBUG',
			'handlers':['ark_chatlog_file','console']
		}
	}
}