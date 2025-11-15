from valutatrade_hub.config import Config
from valutatrade_hub.cli.interface import Engine
from valutatrade_hub.core.log_record import BalanceLogRecord
from valutatrade_hub.logger import Logger
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.api_clients import init_clients
from valutatrade_hub.parser_service.updater import RatesUpdater


if __name__ == '__main__':
    config = Config(
        "/home/hex/git/masters_degree_python_project_3/config.json")
    config.load()
    parser_config = ParserConfig("/home/hex/git/masters_degree_python_project_3/parser_config.json")
    parser_config.load()
    clients = init_clients(parser_config)
    logger_config = Logger(
        "/home/hex/git/masters_degree_python_project_3/"
        "logger_config.json"
    )
    logger_config.load()
    updater = RatesUpdater(parser_config, logger_config, *clients)
    updater.run_update()
    Engine(config, updater).run()
