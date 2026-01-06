from src.app_logs import StructuredLogger, LogLevels, configure_logging, get_logger

def test_structured_logger_info_and_format():
    logger = StructuredLogger('test')
    msg = logger._format_log(LogLevels.info, 'message', user='u')
    assert 'INFO' in msg and 'message' in msg and 'user' in msg
    # info should not raise
    logger.info('info message', key='val')

def test_structured_logger_warning_and_error():
    logger = StructuredLogger('test')
    logger.warning('warn', foo='bar')
    logger.error('err', foo='bar')

def test_structured_logger_debug_and_exception():
    logger = StructuredLogger('test')
    logger.debug('debug', foo='bar')
    try:
        raise ValueError('fail')
    except Exception as e:
        logger.exception('exc', exc_info=e)

def test_configure_logging_and_get_logger():
    configure_logging('DEBUG')
    logger = get_logger('test')
    assert isinstance(logger, StructuredLogger)
