import argparse
import asyncio
import logging
from pprint import pprint

from functions import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")
    # Parse input from console: python3 main.py 3 eur uah plz
    parser = argparse.ArgumentParser(description="Example CLI using argparse")
    parser.add_argument("days", type=int, help="An integer number")
    parser.add_argument(
        "currency", type=str, nargs="*", help="Currency codes (optional)"
    )
    days_quantity = parser.parse_args().days
    currencies_input = parser.parse_args().currency

    r = asyncio.run(main(days_quantity, currencies_input))
    pprint(r)
