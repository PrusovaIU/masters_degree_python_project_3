# Платформа для отслеживания и симуляции торговли валютами
Домашнее задание по предмету "Основы Python". Проект №3

Это комплексная платформа, которая позволяет пользователям регистрироваться, 
управлять своим виртуальным портфелем фиатных и криптовалют, 
совершать сделки по покупке/продаже, а также отслеживать актуальные курсы в реальном времени. 
Система состоит из двух основных сервисов:

* **Сервис Парсинга (Parser Service)**: Отдельное приложение, которое по запросу или 
расписанию обращается к публичным API, получает актуальные курсы, сравнивает их с 
предыдущими значениями и сохраняет историю в базу данных. 

* **Основной Сервис (Core Service)**: Главное приложение, которое предоставляет 
пользовательский интерфейс (CLI), управляет пользователями, их кошельками, историей 
транзакций и взаимодействует с сервисом парсинга для получения актуальных курсов.

## Ключевые технологии и концепции
Проект охватывает широкий спектр тем, необходимых для современной разработки на Python:

* Управление проектом: 
  * Poetry для инициализации, управления зависимостями и сборки пакета. 
  * Makefile для автоматизации рутинных команд.
* Контроль версий: 
  * Git для отслеживания изменений. Рекомендуется вести разработку по методике ветвления 
Gitflow или Github Flow.
* Качество кода: 
  * Ruff для статического анализа и форматирования кода в соответствии со стандартом PEP8.
* Основы Python: Глубокое погружение в объектно-ориентированное программирование. 
* Продвинутые аспекты Python: 
  * Применение try...except для обработки исключений;
  * Использование декораторов для расширения функциональности (логирование, подтверждение 
действий) и замыканий для реализации кэширования.

## Библиотеки и зависимости

* Внешние: 
  * ruff (для разработки), 
  * prettytable (для форматированного вывода).
* Стандартные: 
  * json для работы с файлами.

## Запуск

### Установка зависимостей

Проект использует [Poetry](https://python-poetry.org/) для управления зависимостями. 
Если Poetry у вас ещё не установлен, вы можете установить его следующим образом:

```bash
pip install poetry
```

После установки Poetry выполните команду для установки всех зависимостей:

```bash
poetry install
```

или MakeFile:

```bash
make install
```

### Запуск

Для запуска используйте команду:

```bash
poetry run project --config <путь до файла конфигурации> --ps-config <путь до файла конфигурации PerserService> --loger-config <путь до файла конфигурации логгера>
```

или Makefile:

```bash
make project CONFIG=<путь до файла конфигурации> PS_CONFIG=<путь до файла конфигурации PerserService> LOGGER_CONFIG=<путь до файла конфигурации логгера>
```

### Файл конфигурации

При запуске приложения необходимо передать пути до 3 файлов конфигурации

* основная конфигурация;
* конфигурация для ParserService;
* конфигурация для логгера.
    

#### Основная конфигурация

Шаблон файла:

```json
{
  "data_path": "",
  "base_currency": "",
  "user_passwd_min_length": 4,
  "rates_file_path": "",
  "rates_update_interval": 5
}
```

<table>
    <tr>
        <th>Название параметра</th>
        <th>Тип значений</th>
        <th>Значение по умолчанию</th>
        <th>Описание</th>
    </tr>
    <tr>
        <td>data_path</td>
        <td>str</td>
        <td></td>
        <td>Путь до директории с файлами данных</td>
    </tr>
    <tr>
        <td>base_currency</td>
        <td>str</td>
        <td>USD</td>
        <td>код базовой валюты (в верхнем регистре)</td>
    </tr>
    <tr>
        <td>user_passwd_min_length</td>
        <td>int</td>
        <td>4</td>
        <td>минимальная длинна пароля пользователя</td>
    </tr>
    <tr>
        <td>rates_file_path</td>
        <td>str</td>
        <td></td>
        <td>путь до файла с курсами валют</td>
    </tr>
    <tr>
        <td>rates_update_interval</td>
        <td>int</td>
        <td>5</td>
        <td>интервал обновления курсов в минутах</td>
    </tr>
</table>

#### Конфигурация для ParserService

Шаблон файла:

```json
{
  "coingecko_url": "",
  "exchangerate_api_url": "",
  "exchangerate_api_key": "",
  "base_currency": "",
  "fiat_currencies": ["<код валюты>", ...],
  "crypto_currencies": {
    "<название валюты>": "<код>"
  },
  "request_timeout": 10,
  "max_history_len": 100,
  "data_path": "data_path"
}
```

<table>
    <tr>
        <th>Название параметра</th>
        <th>Тип значений</th>
        <th>Значение по умолчанию</th>
        <th>Описание</th>
    </tr>
    <tr>
        <td>coingecko_url</td>
        <td>str</td>
        <td>https://api.coingecko.com/api/v3/simple/price</td>
        <td>URL сервиса CoinGecko</td>
    </tr>
    <tr>
        <td>exchangerate_api_url</td>
        <td>str</td>
        <td>https://v6.exchangerate-api.com/v6</td>
        <td>URL сервиса с</td>
    </tr>
    <tr>
        <td>exchangerate_api_key</td>
        <td>str</td>
        <td></td>
        <td>ключ для сервиса</td>
    </tr>
    <tr>
        <td>base_currency</td>
        <td>str</td>
        <td>USD</td>
        <td>код базовой валюты (в верхнем регистре)</td>
    </tr>
    <tr>
        <td>fiat_currencies</td>
        <td>list[str]</td>
        <td>["EUR", "GBP", "RUB"]</td>
        <td>список поддерживаемых фиат валют (в верхнем регистре)</td>
    </tr>
    <tr>
        <td>crypto_currencies</td>
        <td>dict</td>
        <td>
            {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "solana": "SOL"
            }
        </td>
        <td>список криптовалют</td>
    </tr>
    <tr>
        <td>request_timeout</td>
        <td>int</td>
        <td>10</td>
        <td>таймаут запросов к клиентам</td>
    </tr>
    <tr>
        <td></td>
        <td>str</td>
        <td>json</td>
        <td>формат логов. Доступные значения: json, str</td>
    </tr>
    <tr>
        <td>max_history_len</td>
        <td>int</td>
        <td>100</td>
        <td>максимальное количество записей в истории</td>
    </tr>
    <tr>
        <td>data_path</td>
        <td>str</td>
        <td></td>
        <td>путь до директории с данными</td>
    </tr>
</table>

#### Конфигурация для логгера

Шаблон файла:

```json
{
  "log_file_name": "",
  "logs_dir_path": "",
  "rotation": "",
  "log_level": "",
  "backup_count": 5,
  "encoding": "",
  "format": ""
}
```

<table>
    <tr>
        <th>Название параметра</th>
        <th>Тип значений</th>
        <th>Значение по умолчанию</th>
        <th>Описание</th>
    </tr>
    <tr>
        <td>log_file_name</td>
        <td>str</td>
        <td></td>
        <td>Название файла с логами</td>
    </tr>
    <tr>
        <td>logs_dir_path</td>
        <td>str</td>
        <td></td>
        <td>путь до директории с логами</td>
    </tr>
    <tr>
        <td>rotation</td>
        <td>str</td>
        <td></td>
        <td>
            ротация. Формат значения: "10 b", "10 kb", "10 mb", "10 gb", "10 tb",
            "10 s", "10 m", "10 h", "10 d"
        </td>
    </tr>
    <tr>
        <td>log_level</td>
        <td>str</td>
        <td>INFO</td>
        <td>уровень логов. Доступные значения: DEBUG, INFO, WARNING, ERROR, CRITICAL ERROR</td>
    </tr>
    <tr>
        <td>backup_count</td>
        <td>int</td>
        <td>5</td>
        <td>максимальное количество файлов с бэкапом</td>
    </tr>
    <tr>
        <td>encoding</td>
        <td>str</td>
        <td>utf-8</td>
        <td>кодирование</td>
    </tr>
    <tr>
        <td>format</td>
        <td>str</td>
        <td>json</td>
        <td>формат логов. Доступные значения: json, str</td>
    </tr>
</table>

## Команды

<table>
    <tr>
        <th>Команда</th>
        <th>Формат</th>
        <th>Описание</th>
    </tr>
    <tr>
        <td>register</td>
        <td>
            register --username <имя пользователя> --password <пароль>
        </td>
        <td>зарегистрировать пользователя</td>
    </tr>
    <tr>
        <td>login</td>
        <td>login --username <имя пользователя> --password <пароль></td>
        <td>авторизоваться</td>
    </tr>
    <tr>
        <td>show-portfolio</td>
        <td>show-portfolio</td>
        <td>показать все кошельки и итоговую стоимость в базовой валюте</td>
    </tr>
    <tr>
        <td>buy</td>
        <td>buy --currency <код валюты> --amount <сумма покупки></td>
        <td>купить валюту</td>
    </tr>
    <tr>
        <td>sell</td>
        <td>sell --currency <код валюты> --amount <сумма покупки></td>
        <td>продать валюты</td>
    </tr>
    <tr>
        <td>get-rate</td>
        <td>get-rate --from <код валюты> --to <код валюты></td>
        <td>получить текущий курс одной валюты к другой</td>
    </tr>
    <tr>
        <td>update-rates</td>
        <td>update-rates [--source <имя источника>]</td>
        <td>
            запустить немедленное обновление курсов валют. Если указано имя источника, то будут обновлены только 
            валюты, полученные из данного источника
        </td>
    </tr>
    <tr>
        <td>show-rates</td>
        <td>show-rates --currency <код валюты> | --top <количество строк> | --base <код валюты></td>
        <td>
            показать список актуальных курсов из локального кеша с возможностью фильтрации.
            Если указан параметр currency, то будет выведен курс только для указанной валюты по отношению к базовой.
            Если указан параметр top, то будут выведены N самых дорогих валют.
            Если указан параметр base, то будут выведены все курсы относительно указанной базы.
        </td>
    </tr>
</table>

## Демонстрация

### Регистрация

[![asciicast](https://asciinema.org/a/DuHf3xwJtHH7ITrhM1TLxS9hv.svg)](https://asciinema.org/a/DuHf3xwJtHH7ITrhM1TLxS9hv)
