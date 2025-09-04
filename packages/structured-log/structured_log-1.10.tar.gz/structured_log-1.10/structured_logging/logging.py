import logging
import structlog
import ctypes
import pathlib

def add_module_and_lineno(logger: logging.Logger, method_name: str, event_dict: dict):
    try:
        frame, module_str = structlog._frames._find_first_app_frame_and_name(additional_ignores=[__name__])
        event_dict['module'] = module_str
        event_dict['lineno'] = frame.f_lineno
    except:
        pass
    return event_dict

try:
    dir = pathlib.Path(__file__).parent.resolve()
    libc = ctypes.cdll.LoadLibrary(str(dir / "structured_logging.pyd"))
    log = libc.Log
    log.argtypes = [ctypes.c_char_p]
except:
    log = lambda x: x

def set_logger(filename):
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt='iso'),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                add_module_and_lineno,
                elastic_format,
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ]
        )
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

def elastic_format(logger: logging.Logger, method_name: str, event_dict: dict):
    # Elastic requires the message to be under 'message' and not under 'event'
    try:
        if isinstance(event_dict, dict) and 'event' in event_dict:
            log(event_dict.get('event').encode('utf-8'))
    except:
        pass

    return event_dict
