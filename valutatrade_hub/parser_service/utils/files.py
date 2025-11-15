import tempfile
from json import JSONDecodeError, dumps
from pathlib import Path

from valutatrade_hub.logger import Logger
from valutatrade_hub.logging_config.log_record import LogRecord


def write_file(path: Path, data: dict | list, action_name: str):
    logger = Logger().logger()
    log_message = {"path": str(path.absolute())}
    try:
        with tempfile.NamedTemporaryFile(
                suffix=".json",
                delete=False
        ) as tmp_file:
            temp_filename = Path(tmp_file.name)
            data = dumps(data, indent=4)
            tmp_file.write(data.encode())
        temp_filename.rename(path)
    except (OSError, JSONDecodeError) as e:
        logger.error(
            LogRecord(
                action=action_name,
                result="error",
                error_type=e.__class__.__name__,
                message=log_message
            )
        )
    else:
        logger.info(
            LogRecord(
                action=action_name,
                result="success",
                message=log_message
            )
        )