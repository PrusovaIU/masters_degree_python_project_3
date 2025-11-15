import logging
from functools import wraps

from valutatrade_hub.logging_config.log_record import LogRecord
from .log_record import BalanceLogRecord
from ..logger import Logger
from .models.operation_info import OperationInfo


_SUCCESS = "OK"
_ERROR = "ERROR"


def log_action(verbose: str | None = None):
    verbose = verbose if verbose else ""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_info = _get_operation_info(*args, **kwargs)
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                log = _error_log(
                    verbose, operation_info, func.__name__, e
                )
                log_level = logging.ERROR
                raise e
            else:
                log = _success_log(
                    verbose, operation_info, func.__name__
                )
                log_level = logging.INFO
            finally:
                logger: logging.Logger = Logger().logger()
                logger.log(log_level, log)
            return result
        return wrapper
    return decorator


def _error_log(
        verbose: str,
        operation_info: OperationInfo | None,
        func_name: str,
        error: Exception
) -> LogRecord:
    if operation_info:
        return BalanceLogRecord(
            action=operation_info.operation_type.value,
            result=_ERROR,
            error_type=error.__class__.__name__,
            error_message=str(error),
            message=verbose,
            username=operation_info.username,
            user_id=operation_info.user_id,
            currency_code=operation_info.currency_code,
            amount=operation_info.amount,
            rate=operation_info.rate,
            base=operation_info.base_currency
        )
    else:
        return LogRecord(
            action=func_name,
            result=_ERROR,
            error_type=error.__class__.__name__,
            error_message=str(error)
        )


def _success_log(
        verbose: str,
        operation_info: OperationInfo | None,
        func_name: str
) -> LogRecord:
    """
    Формирование лога об успешной операции.

    :param verbose: Инфорационное сообщение.
    :param func_name: имя декорируемой функции.
    :return: лог.
    """
    if operation_info:
        return BalanceLogRecord(
            action=operation_info.operation_type.value,
            result=_SUCCESS,
            message=verbose,
            username=operation_info.username,
            user_id=operation_info.user_id,
            currency_code=operation_info.currency_code,
            amount=operation_info.amount,
            rate=operation_info.rate,
            base=operation_info.base_currency
        )
    else:
        return LogRecord(
            action=func_name,
            result=_SUCCESS,
            message=verbose
        )

def _get_operation_info(*args, **kwargs) -> OperationInfo | None:
    operation_info = [
        arg for arg in (*args, *kwargs.values())
        if isinstance(arg, OperationInfo)
    ]
    if operation_info:
        return operation_info[0]
    return None
