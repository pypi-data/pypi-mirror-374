import inspect
import logging
from typing import Callable, Any, List, Dict

from sirius import common
from sirius.archive.application_performance_monitoring.constants import Operation


# logging.basicConfig(level=logging.DEBUG, format="%(asctime)s || %(levelname)s || %(module)s.%(funcName)s\n%(message)s\n")


# sentry_sdk.init(
#     dsn=common.get_environmental_secret(EnvironmentSecret.SENTRY_URL),
#     traces_sample_rate=1.0,
#     profiles_sample_rate=1.0,
#     environment=common.get_environment().value,
#     integrations=[
#         LoggingIntegration(
#             level=logging.DEBUG,
#             event_level=logging.ERROR
#         ),
#     ],
# )


def transaction(operation: Operation, transaction_name: str) -> Callable:
    def decorator(function: Callable) -> Callable:
        def wrapper(*args: List[Any], **kwargs: Dict[str, Any]) -> Any:
            if common.is_ci_cd_pipeline_environment() or common.is_development_environment():
                return function(*args, **kwargs)
            else:
                # with sentry_sdk.start_transaction(op=operation.value, name=transaction_name):
                result: Any = function(*args, **kwargs)
            return result

        return wrapper

    return decorator


def get_logger() -> logging.Logger:
    return logging.getLogger(get_name_of_calling_module())


def get_name_of_calling_module() -> str:
    file_path: str = inspect.getmodule(inspect.stack()[2][0]).__file__
    file_name: str = file_path.split("\\")[-1] if "\\" in file_path else file_path.split("/")[-1]
    return file_name.replace(".py", "")
