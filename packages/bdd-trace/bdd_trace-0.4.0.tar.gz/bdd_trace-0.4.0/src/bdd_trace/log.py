import sys
from logging import INFO, Formatter, Handler, LogRecord, StreamHandler, getLogger
from logging.handlers import QueueHandler, QueueListener
from queue import Queue

from opentelemetry.sdk._logs import LoggingHandler

from bdd_trace.trace import Profile

_log_queue: Queue | None = None
_log_listener: QueueListener | None = None


def setup_logging(
    profile: Profile,
    modules: list[str],
    level: str | int = INFO,
    trace_id_format: str = "%(asctime)s|%(levelname)s|%(name)s|%(otelTraceID)s|%(message)s",
    no_trace_id_format: str = "%(asctime)s|%(levelname)s|%(name)s|%(message)s",
) -> None:
    global _log_queue, _log_listener
    if _log_queue is not None or _log_listener is not None:
        raise RuntimeError("logging is already setup")

    root_logger = getLogger()
    root_logger.handlers = []

    _log_queue = Queue(1000)
    for module in modules:
        _setup_module_logger(level, module)

    format = trace_id_format if profile == Profile.NO_TRACE else no_trace_id_format
    console_handler = _create_console_handler(modules, format)
    log_process_handlers = [console_handler]
    if profile != Profile.NO_TRACE:
        otel_handler = LoggingHandler()
        log_process_handlers.append(otel_handler)

    _log_listener = QueueListener(_log_queue, *log_process_handlers)
    _log_listener.start()


def stop_logging() -> None:
    global _log_queue, _log_listener
    if _log_listener is not None:
        _log_listener.stop()
    _log_listener = None
    _log_queue = None


def _create_console_handler(modules: list[str], format: str) -> Handler:
    class ModulePrefixFilter:
        def __init__(self, module_prefixes: list[str]):
            self.module_prefixes: set[str] = set(module_prefixes)
            self.module_prefixes_with_dot: tuple[str, ...] = tuple(f"{prefix}." for prefix in module_prefixes)

        def filter(self, record: LogRecord) -> bool:
            return record.name in self.module_prefixes or record.name.startswith(self.module_prefixes_with_dot)

    handler = StreamHandler(sys.stderr)
    handler.setFormatter(Formatter(format))
    handler.addFilter(ModulePrefixFilter(modules))
    return handler


def _setup_module_logger(level: str | int, module: str) -> None:
    class SingleLineFormatter(Formatter):
        def formatMessage(self, record: LogRecord) -> str:
            return super().formatMessage(record).replace("\n", " ").replace("\r", "")

    logger = getLogger(module)
    logger.setLevel(level)
    logger.propagate = False

    queue = _log_queue
    if queue is None:
        raise RuntimeError("log queue is not initialized")
    handler = QueueHandler(queue)
    handler.setFormatter(SingleLineFormatter())
    logger.handlers = [handler]
