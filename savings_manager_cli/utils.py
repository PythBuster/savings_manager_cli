import locale as lc
import sys
from datetime import datetime
from typing import Sequence

import pytz
import tabulate


def int_or_none(raw: str) -> int | None:
    return None if raw == "None" else int(raw)


def exit_with_error(content: dict) -> None:
    # TODO: parse error doct to console representation
    print(content, file=sys.stderr)
    sys.exit(1)


def tabulate_str(headers: Sequence, rows: Sequence, showindex: bool = False) -> str:
    return tabulate.tabulate(
        headers=headers,
        tabular_data=rows,
        tablefmt="rounded_outline",
        showindex=showindex,
    )


def localize_datetime(
    dt: datetime,
    locale: str = "de_DE.utf8",
    timezone: str = "Europe/Berlin",
) -> str:
    lc.setlocale(lc.LC_ALL, locale)
    tz = pytz.timezone(zone=timezone)
    return dt.astimezone(tz).strftime("%c")


def colorize_number(key, value) -> str:
    if key not in ["amount", "balance"]:
        return value

    if value < 0:
        return f"\033[91m{value}\033[0m"

    return f"\u001b[32m{value}\033[0m"
