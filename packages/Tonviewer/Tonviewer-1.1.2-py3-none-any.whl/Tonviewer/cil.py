import argparse
import asyncio
from .Scraping import Scraping
from .main import help , versions

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TON Crypto Info Scraper is a Python library that allows you to fetch ( real-time balance of wallet , transactions , price ) data without needing any APIs.",
        add_help=False
    )
    parser.add_argument("-b", "--balance", type=str, help=" Prints balance of wallet")
    parser.add_argument("-p", "--price", type=str, help="Prints live price #ex: toncoin , bitcoin , ...")
    parser.add_argument("-t" , "--transactions" , type=str, help= "get transactions of Wallet")
    parser.add_argument("-l", "--limit", type=int, help="Number of times to get transactions")
    parser.add_argument("-h", "--help", action="store_true", help="Display help message")
    parser.add_argument("-v", "--version", action="store_true", help="Display version info")


    args, unknown = parser.parse_known_args()

    if unknown:
        for arg in unknown:
            print(f"[ERROR] Argument `{arg}` not recognized.")
        exit(1)

    return args


async def run_cli():
    args = parse_args()

    try:
        if args.balance:
            print(Scraping().get_tonviewer(args.balance))

        elif args.price:
            print(Scraping().get_coingecko_price(args.price))

        elif args.transactions:
            print(Scraping().get_transactions(args.transactions , args.limit))

        elif args.help:
            print(help())

        elif args.version:
            print(versions())

        else:
            print("[ERROR] No valid arguments provided. Use `-h` for help.")
    except Exception as e:
        print(f"[FATAL] Unexpected error: {e}")


def console():
    asyncio.run(run_cli())


if __name__ == "__main__":
    console()
