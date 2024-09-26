import argparse
from datetime import datetime
from typing import Optional
from implementation import CONFIG


class Arguments:
    def __init__(self, namespace: argparse.Namespace) -> None:
        self._namespace = namespace

    @property
    def api_key(self) -> str:
        assert self._namespace.api_key
        return self._namespace.api_key

    @property
    def sheet_id(self) -> str:
        assert self._namespace.sheet_id
        return self._namespace.sheet_id

    @property
    def log_date(self) -> Optional[datetime]:
        return self._namespace.log_date

    @property
    def no_upload(self) -> bool:
        return self._namespace.no_upload


def parse_arguments() -> Arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--log-date",
        action="store",
        type=datetime.fromisoformat,
        help="Optional date to use as date of log. In ISO format (e.g. '2024-09-26T20:26:18'); do not use timezones",
    )
    parser.add_argument(
        "-s",
        "--sheet-id",
        action="store",
        type=str,
        required=True,
        help="ID of the sheet in which needs to be updated.",
    )
    parser.add_argument(
        "-a",
        "--api-key",
        action="store",
        type=str,
        help="Google maps API key to use. If not present will attempt to load api_key.txt.",
    )
    parser.add_argument(
        "--no-upload",
        action="store_false",
        help="Disable upload to the sheet.",
    )
    namespace = parser.parse_args()
    if not namespace.api_key:
        with open("api_key.txt", "r", encoding="utf-8") as api:
            api_key = api.readline()
    namespace.api_key = api_key
    args = Arguments(namespace)
    CONFIG.upload = args.no_upload
    return args
