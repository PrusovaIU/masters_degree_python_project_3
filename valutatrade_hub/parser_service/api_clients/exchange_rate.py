from typing import Any

from .abc import BaseApiClient
from valutatrade_hub.parser_service import models
import requests
from datetime import datetime
from http import HTTPStatus


class ExchangeRateApiClient(BaseApiClient):
    @property
    def info(self) -> dict[str, str]:
        return {
            "name": "ExchangeRateApi",
            "url": self._config.exchangerate_api_url
        }

    def _call_api(self) -> list[models.ExchangeRate]:
        url = (f"{self._config.exchangerate_api_url}/"
               f"{self._config.exchangerate_api_key}"
               f"/latest/{self._config.base_currency}")
        response, lead_time = self._request(url)
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
        for currency, rate_value in response.json()["rates"].items():
            rate = models.ExchangeRate(
                from_currency=self._config.base_currency,
                to_currency=currency,
                rate=rate_value,
                timestamp=now,
                source="ExchangeRateApi",
                meta=models.ExchangeRateMeta(
                    raw_id=currency,
                    request_ms=request_ms,
                    status_code=HTTPStatus(response.status_code)
                )
            )
            rates.append(rate)
        return rates
