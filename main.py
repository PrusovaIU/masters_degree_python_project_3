from valutatrade_hub.config import Config
from valutatrade_hub.cli.interface import Engine
from valutatrade_hub.logging_config import LoggingConfig, LogRecord


if __name__ == '__main__':
    # config = Config(
    #     "/home/hex/git/masters_degree_python_project_3/config.json")
    # config.load()
    # Engine(config).run()
    logger_config = LoggingConfig(
        "/home/hex/git/masters_degree_python_project_3/"
        "logger_config.json"
    )
    logger_config.load()
    logger = logger_config.logger("action")
    logger.info(
        LogRecord(
            action="test",
            username="user",
            user_id=1,
            result="success"
        )
    )

