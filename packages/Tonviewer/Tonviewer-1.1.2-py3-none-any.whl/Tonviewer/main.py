from importlib.metadata import version, PackageNotFoundError

def help():
    return """
Tonviewer -[OPTIONS] "[FOR-OPTION]"

Options
    -b, --balance                   Prints balance of wallet .
    -p, --price                     Prints live price #ex: toncoin , bitcoin , ... .
    -t, --transactions              Get transactions of Wallet . 
    -l, --limit                     Number of times to get transactions .
    -h, --help                      Display help message .
    -v, --version                   Show Version Of Libarary and info .
"""

def versions():
    try:
        pkg_version = version("Tonviewer")
    except PackageNotFoundError:
        pkg_version = "unknown"

    return f"""
SyncAi Version: {pkg_version} .
Author: PyCodz Channel .
(PyPi) : https://pypi.org/project/Tonviewer .
(Telegram) : https://t.me/PyCodz .
(My Portfolio) : https://deep.is-a.dev .
"""