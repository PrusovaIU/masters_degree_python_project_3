from valutatrade_hub.cli.interface import Engine
from valutatrade_hub.core.config import Config


if __name__ == '__main__':
    # Engine().run()
    config = Config("/home/hex/git/masters_degree_python_project_3/config.json")
    config.load()
    print(config.path)
    print(config.data_path)
    print(config.base_currency)
    print("------")
    config = Config("1111")
    print(config.path)
    print(config.data_path)
    print(config.base_currency)
    print(config.user_passwd_min_length)
