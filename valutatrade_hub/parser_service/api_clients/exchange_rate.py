from datetime import datetime
from http import HTTPStatus

import requests

from valutatrade_hub.parser_service import models

from .abc import ApiClientInfo, BaseApiClient


class ExchangeRateApiClient(BaseApiClient):
    @property
    def info(self) -> ApiClientInfo:
        return ApiClientInfo(
            name="ExchangeRateApi",
            url=self._config.exchangerate_api_url
        )

    def _call_api(self) -> list[models.ExchangeRate]:
        currencies = {
            self._config.base_currency,
            *self._config.fiat_currencies
        }
        currencies = list(currencies)
        result: list[models.ExchangeRate] = []
        for i, from_currency in enumerate(currencies):
            url = (f"{self._config.exchangerate_api_url}/"
                   f"{self._config.exchangerate_api_key}"
                   f"/latest/{from_currency}")
            response, lead_time = self._request(url)
            rates = self._parse_response(
                response, lead_time, from_currency, currencies[i+1:]
            )
            result.extend(rates)
        return result

    @staticmethod
    def _parse_response(
            response: requests.Response,
            request_ms: int,
            from_currency: str,
            to_currencies: list[str]
    ) -> list[models.ExchangeRate]:
        """
        Парсинг ответа от API.

        :param response: ответ от API.
        :param request_ms: время выполнения запроса.
        :param from_currency: исходная валюта.
        :param to_currencies: список валют для конвертации.

        :return: список курсов валют для журнала.
        """
        now = datetime.now()
        rates = []
        response_data = response.json()["conversion_rates"]
        filtered_data = {
            currency: rate_value
            for currency, rate_value in response_data.items()
            if currency in to_currencies}
        for currency, rate_value in filtered_data.items():
            rate = models.ExchangeRate(
                from_currency=from_currency,
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
