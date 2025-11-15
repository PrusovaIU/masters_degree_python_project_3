from valutatrade_hub.config import Config
from valutatrade_hub.cli.interface import Engine
from valutatrade_hub.logger import Logger
from valutatrade_hub.parser_service.config import ParserConfig
from valutatrade_hub.parser_service.api_clients import init_clients
from valutatrade_hub.parser_service.updater import RatesUpdater
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description="ValutaTrade Hub")
    parser.add_argument(
        "--config",
        type=str,
        dest="config",
        required=True,
        help="Путь к файлу конфигурации"
    )
    parser.add_argument(
        "--ps-config",
        type=str,
        dest="ps_config",
        required=True,
        help="Путь к файлу конфигурации парсера"
    )
    parser.add_argument(
        "--logger-config",
        type=str,
        dest="logger_config",
        required=True,
        help="Путь к файлу конфигурации логгера"
    )
    args = parser.parse_args()
    run(args.config, args.ps_config, args.logger_config)


def run(
        config_path: str,
        ps_config_path: str,
        logger_config_path: str
):
    config = Config(config_path)
    config.load()
    parser_config = ParserConfig(ps_config_path)
    parser_config.load()
    logger = Logger(logger_config_path)
    logger.load()
    updater = _init_parser_service(parser_config, logger)
    try:
        Engine(config, updater).run()
    except KeyboardInterrupt:
        print("Завершение работы...")


def _init_parser_service(
        parser_config: ParserConfig,
        logger: Logger
) -> RatesUpdater:
    clients = init_clients(parser_config)
    updater = RatesUpdater(parser_config, logger, *clients)
    updater.run_update()
    return updater


if __name__ == '__main__':
    main()
