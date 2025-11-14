from typing import Any

import requests

from .abc import BaseApiClient
from valutatrade_hub.parser_service import models
from datetime import datetime

from http import HTTPStatus


class CoinGeckoClient(BaseApiClient):
    @property
    def info(self) -> dict[str, str]:
        return {
            "name": "CoinGecko",
            "url": self._config.coingecko_url
        }

    def _call_api(self) -> list[models.ExchangeRate]:
        params = {
            "ids": ",".join((self._config.crypto_currencies.values())),
            "vs_currencies": self._config.base_currency
        }
        response, lead_time = self._request(
            self._config.coingecko_url,
            params=params
        )
        return self._parse_response(response, lead_time)

    def _parse_response(
            self,
            response: requests.Response,
            request_ms: int
    ) -> list[models.ExchangeRate]:
        """
        Парсинг ответа от API.

        :param response: ответ от API.
        :param request_ms: время выполнения запроса.
        :return: список курсов валют для журнала.
        """
        now = datetime.now()
        rates = []
        for currency, data in response.json().items():
            rate_value: float = 1 / data[self._config.base_currency]
            rate = models.ExchangeRate(
                from_currency=self._config.base_currency,
                to_currency=self._config.crypto_currencies[currency],
                rate=rate_value,
                timestamp=now,
                source="CoinGecko",
                meta=models.ExchangeRateMeta(
                    raw_id=currency,
                    request_ms=request_ms,
                    status_code=HTTPStatus(response.status_code)
                )
            )
            rates.append(rate)
        return rates
