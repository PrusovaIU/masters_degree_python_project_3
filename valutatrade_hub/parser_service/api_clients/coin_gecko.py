import requests

from .abc import BaseApiClient
from valutatrade_hub.parser_service import models
from valutatrade_hub.parser_service.config import CONFIG
from datetime import datetime
from time import time
from http import HTTPStatus


class CoinGeckoClient(BaseApiClient):
    def _request(self) -> list[models.ExchangeRate]:
        params = {
            "ids": ",".join((CONFIG.crypto_currencies.values())),
            "vs_currencies": CONFIG.base_currency
        }
        start = time()
        response: requests.Response = requests.get(
            CONFIG.coingecko_url,
            params=params,
            timeout=self._request_timeout
        )
        end = time()
        response.raise_for_status()
        return self._parse_response(response, int((end - start) * 1000))

    @staticmethod
    def _parse_response(
            response: requests.Response,
            request_ms: int
    ) -> list[models.ExchangeRate]:
        now = datetime.now()
        rates = []
        for currency, data in response.json().items():
            rate_value: float = data[CONFIG.base_currency]
            rate = models.ExchangeRate(
                from_currency=CONFIG.crypto_currencies[currency],
                to_currency=CONFIG.base_currency,
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
