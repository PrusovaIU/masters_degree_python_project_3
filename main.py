from valutatrade_hub.config import Config
from valutatrade_hub.cli.interface import Engine


if __name__ == '__main__':
    config = Config(
        "/home/hex/git/masters_degree_python_project_3/config.json")
    config.load()
    Engine(config).run()

