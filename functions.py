import asyncio
import logging
import sys
from datetime import date, timedelta

import aiohttp

BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="
DEFAULT_CURRENCIES = ["EUR", "USD"]


def get_urls(qnty: int) -> set:
    """
    creates set of urls
    """
    urls = set()
    today = date.today()
    if 0 < qnty <= 10:
        for i in range(qnty):
            date_for_url = today - timedelta(days=i)
            urls.add(BASE_URL + date_for_url.strftime("%d.%m.%Y"))
        return urls
    else:
        print("Enter days quantity between 1 and 10")
        sys.exit()


def get_currencies_list(cur_list=None):
    """
    creates list of currencies
    """
    currencies_list = DEFAULT_CURRENCIES
    if cur_list:
        currencies_list.extend([x.upper() for x in cur_list])
    return currencies_list


async def get_currency_rate(
    url: str,
    currencies,
    session,
) -> dict:
    """
    get currencies rate from privatbank api
    """
    url = url
    currencies = get_currencies_list(currencies)
    dict_currency = {}
    logging.info(f"Starting {url}")
    try:
        async with session.get(url, ssl=False) as response:
            if response.status == 200:
                all_data = await response.json()
                one_day_currencies = {
                    i["currency"]: {
                        "sale": i["saleRateNB"],
                        "purchase": i["purchaseRateNB"],
                    }
                    for i in all_data["exchangeRate"]
                    if i.get("currency") in currencies
                }
                dict_currency = {all_data["date"]: one_day_currencies}
            else:
                print(f"Error status: {response.status} for {url}")
    except aiohttp.ClientConnectorError as err:
        print(f"Connection error: {url}", str(err))
    return dict_currency


async def main(days_quantity: int, currencies):
    result = []

    async with aiohttp.ClientSession() as session:
        for url in get_urls(days_quantity):
            result.append(get_currency_rate(url, currencies, session))
        return await asyncio.gather(*result)
