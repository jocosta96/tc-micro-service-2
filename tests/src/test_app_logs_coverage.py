from src import app_logs

import logging
from io import StringIO

class TestAppLogs:

    def setup_method(self):
        # Configura o logger para StringIO
        self.logger = app_logs.get_logger('test_logger')
        self.log_stream = StringIO()
        handler = logging.StreamHandler(self.log_stream)
        handler.setLevel(logging.INFO)
        self.logger.logger.handlers = [handler]
        self.logger.logger.setLevel(logging.INFO)

    def test_log_info(self):
        # Given mensagem
        self.logger.info('info test')
        # Then mensagem aparece no log_stream (formato JSON)
        output = self.log_stream.getvalue()
        assert 'info test' in output

    def test_log_error(self):
        # Given mensagem
        self.logger.logger.setLevel(logging.ERROR)
        self.logger.error('error test')
        # Then mensagem aparece no log_stream (formato JSON)
        output = self.log_stream.getvalue()
        assert 'error test' in output
