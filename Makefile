install:
    poetry install

project:
    poetry run project --config $(CONFIG_PATH) --ps-config $(PS_CONFIG) --logger-config $(LOGGER_CONFIG)

build:
    poetry build

publish:
    poetry publish --dry-run

package-install:
    python3 -m pip install dist/*.whl

lint:
    poetry run ruff check .