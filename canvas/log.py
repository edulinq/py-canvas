import logging

DEFAULT_LOGGING_LEVEL = logging.getLevelName(logging.WARNING)
DEFAULT_LOGGING_FORMAT = '%(asctime)s [%(levelname)-8s] - %(filename)s:%(lineno)s -- %(message)s'

LEVELS = [
    logging.getLevelName(logging.DEBUG),
    logging.getLevelName(logging.INFO),
    logging.getLevelName(logging.WARNING),
    logging.getLevelName(logging.ERROR),
    logging.getLevelName(logging.CRITICAL),
]

def init(level = DEFAULT_LOGGING_LEVEL, format = DEFAULT_LOGGING_FORMAT, **kwargs):
    """
    Initialize or re-initialize the logging infrastructure.
    """

    logging.basicConfig(level = level, format = format, force = True)

    # Ignore logging from third-party libraries.
    logging.getLogger("urllib3").setLevel(logging.WARNING)

# Load the default logging when this module is loaded.
init()
