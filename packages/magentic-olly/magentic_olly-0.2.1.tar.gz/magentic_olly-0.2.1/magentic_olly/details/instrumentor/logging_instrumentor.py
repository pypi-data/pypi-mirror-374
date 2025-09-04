import logging
from typing import Optional
from opentelemetry._logs import get_logger_provider
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry._logs import LoggerProvider as APILoggerProvider, Logger as APILogger
from opentelemetry.instrumentation.logging import LoggingInstrumentor as InjectLoggingInstrumentor
from opentelemetry.util.types import Attributes

class LoggingInstrumentor(BaseInstrumentor):
    _original_get_logger = logging.getLogger
    _handler_name = 'magentic-logging-handler'
    _trace_inject_instrumentor = InjectLoggingInstrumentor()

    _original_make_record = logging.Logger.makeRecord
    _original_warning_fcn = logging.Logger.warning

    def instrumentation_dependencies(self):
        return []
    
    def _instrument(self, **kwargs):
        logging.getLogger = self._instrumented_get_logger
        if not self._trace_inject_instrumentor.is_instrumented_by_opentelemetry:
            self._trace_inject_instrumentor.instrument()
        logging.Logger.makeRecord = self._makeRecord
        logging.Logger.warning = LoggingInstrumentor._warning_fcn
        logging.Logger.warn = LoggingInstrumentor._warning_fcn
        
    def _uninstrument(self, **kwargs):
        logging.getLogger = LoggingInstrumentor._original_get_logger
        logging.Logger.makeRecord = LoggingInstrumentor._original_make_record
        logging.Logger.warning = LoggingInstrumentor._original_warning_fcn
        logging.Logger.warn = LoggingInstrumentor._original_warning_fcn
        if self._trace_inject_instrumentor.is_instrumented_by_opentelemetry:
            self._trace_inject_instrumentor.uninstrument()

    def _instrumented_get_logger(self, *args, **kwargs):
        provider = _LazyLoadedProvider()
        handler = None
        logger: logging.RootLogger = LoggingInstrumentor._original_get_logger(*args, **kwargs)

        if logger.name and (logger.name == 'root' or logger.name.startswith("opentelemetry")):
            return logger
        handler = LoggingHandler(logger_provider=provider)
        handler.name = LoggingInstrumentor._handler_name
        if not any(h.name == LoggingInstrumentor._handler_name for h in logger.handlers):
            logger.addHandler(handler)
        return logger
    
    
    @staticmethod
    def _makeRecord(*args, **kwargs):
        logger = args[0]
        if logger.name and (logger.name == 'root'):
            return LoggingInstrumentor._original_make_record(*args, **kwargs)
        extra = kwargs.get('extra', None)
        if extra is None and len(args) > 10:
            extra = args[9]
        if extra and isinstance(extra, dict):
            for key in extra:
                value = extra[key]
                if isinstance(value, (str, int, float, bool)):
                    extra[key] = value
                else:
                    extra[key] = str(value)
        return LoggingInstrumentor._original_make_record(*args, **kwargs)
    
    @staticmethod
    def _warning_fcn(self, msg, *args, **kwargs):
        blackluist = ["force_flush"]
        if any(kw in msg for kw in blackluist):
            # Skip logging this message if it contains 'force_flush'
            return
        return LoggingInstrumentor._original_warning_fcn(self, msg, *args, **kwargs)


class _LazyLoadedProvider(APILoggerProvider):
    def get_logger(
        self,
        name: str,
        version: Optional[str] = None,
        schema_url: Optional[str] = None,
        attributes: Optional[Attributes] = None,
    ) -> APILogger:
        provider = get_logger_provider()
        return provider.get_logger(name, version, schema_url, attributes)
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        provider = get_logger_provider()
        if not hasattr(provider, 'force_flush'):
            return True
        return provider.force_flush(timeout_millis)