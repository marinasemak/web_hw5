import argparse
import asyncio
import logging
import sys
from datetime import date, timedelta
from pprint import pprint

import aiohttp

BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

parser = argparse.ArgumentParser(description="Example CLI using argparse")
parser.add_argument("days", type=int, help="An integer number")
parser.add_argument("currency", type=str, nargs="*", help="Currency codes")
days_quantity = parser.parse_args().days
currencies = parser.parse_args().currency
print(currencies)

today = date.today()

urls = []
if 0 < days_quantity <= 10:
    for i in range(days_quantity):
        date_for_url = today - timedelta(days=i)
        urls.append(BASE_URL + date_for_url.strftime("%d.%m.%Y"))
else:
    print("Enter days quantity between 1 and 10")
    sys.exit()


async def get_currency(url: str, session) -> dict:
    url = url
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
                    if i.get("currency") == "EUR" or i.get("currency") == "USD"
                }
                dict_currency = {all_data["date"]: one_day_currencies}
            else:
                print(f"Error status: {response.status} for {url}")
    except aiohttp.ClientConnectorError as err:
        print(f"Connection error: {url}", str(err))
    return dict_currency


async def main():
    result = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            result.append(get_currency(url, session))
        return await asyncio.gather(*result)


if __name__ == "__main__":
    r = asyncio.run(main())
    pprint(r)
