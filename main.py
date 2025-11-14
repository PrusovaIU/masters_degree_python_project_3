from valutatrade_hub.config import Config
from valutatrade_hub.cli.interface import Engine
from valutatrade_hub.core.logger import BalanceLogRecord, Logger


if __name__ == '__main__':
    config = Config(
        "/home/hex/git/masters_degree_python_project_3/config.json")
    config.load()
    logger_config = Logger(
        "/home/hex/git/masters_degree_python_project_3/"
        "logger_config.json"
    )
    logger_config.load()
    Engine(config).run()
    # logger_config = Logger(
    #     "/home/hex/git/masters_degree_python_project_3/"
    #     "logger_config.json"
    # )
    # logger_config.load()
    # logger = logger_config.logger("action")
    # logger.info(
    #     BalanceLogRecord(
    #         action="test",
    #         username="user",
    #         user_id=1,
    #         result="success"
    #     )
    # )
    # logger.warning(
    #     BalanceLogRecord(
    #         action="test",
    #         username="user",
    #         user_id=1,
    #         result="success",
    #         message="test",
    #         amount=100.654436
    #     )
    # )
    # logger.error(
    #     BalanceLogRecord(
    #         action="test",
    #         username="user",
    #         user_id=1,
    #         result="error",
    #         error_type=TypeError.__name__,
    #         error_message="test"
    #     )
    # )

