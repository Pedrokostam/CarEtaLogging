from datetime import datetime
import sys
from typing import Optional
import googlemaps
from alive_progress import alive_bar, alive_it, config_handler

from implementation import coords
from implementation.archiver import Archiver, add_row_with_current_time, routes_to_dict
from implementation.request import Request

config_handler.set_global(
    monitor=False,
    elapsed="{elapsed}",
    elapsed_end="(took {elapsed})",
    spinner_length=5,
    bar=None,
    stats=False,
    stats_end=False,
)


home = (50.30442699863767, 19.183934458803197)
work = (50.27773270036598, 18.687399321484765)

endpoints = {"start": home, "end": work}

DTS_WAYPOINTS: list[str | coords] = [
    (50.27057254692684, 18.997468954488145),  # Silesia CC
    (50.28634534657515, 18.75761920992521),  # DTŚ przed Gliwicami
]

A4_WAYPOINTS: list[str | coords] = [
    (50.24520970613863, 19.03422029867627),  # Trzy Stawy
    (50.26927593183539, 18.76631620645797),  # A4 przed zjazdem
]

S86_WAYPOINTS: list[str | coords] = [
    (50.300643605347425, 19.15654892699051),  # OSZOŁOM
    (50.26649709372005, 19.05295016568546),  # IKEA
]

SOSNOWIEC_WAYPOINTS: list[str | coords] = [
    (50.29199710886777, 19.163204488572383),  # 3 Maja za Blachnickiego
    (50.27685469746638, 19.12438491770257),  # Rondo Praw Kobiet
]

S1_WAYPOINTS: list[str | coords] = [
    (50.284299099038556, 19.216300705465596),  # Tuż za wjazdem
    (50.21052546717317, 19.154564592767706),  # Po zjeździe na A4
]


S86_A4 = Request(
    **endpoints,
    waypoints=S86_WAYPOINTS + A4_WAYPOINTS,
    name=["S86", "A4"],
)
SC_A4 = Request(
    **endpoints,
    waypoints=SOSNOWIEC_WAYPOINTS + A4_WAYPOINTS,
    name=["Sc", "A4"],
)
S86_DTS = Request(
    **endpoints,
    waypoints=S86_WAYPOINTS + DTS_WAYPOINTS,
    name=["S86", "DTŚ"],
)
SC_DTS = Request(
    **endpoints,
    waypoints=SOSNOWIEC_WAYPOINTS + DTS_WAYPOINTS,
    name=["Sc", "DTŚ"],
)

S1_A4 = Request(
    **endpoints,
    waypoints=S1_WAYPOINTS + A4_WAYPOINTS,
    name=["S1", "A4"],
)
HOME_WORK = "Dom→Praca"
WORK_HOME = "Praca→Dom"


def update_routes(
    archiver: Archiver,
    maps_client: googlemaps.Client,
    sheet_name: str,
    requests: list[Request],
    *,
    reverse: bool = False,
    forced_time: Optional[datetime] = None,
):
    if reverse:
        requests = [a.reversed() for a in requests]
    p_bar = alive_it(requests, title=f"Getting routes for {sheet_name}")
    routes = []
    for req in p_bar:
        p_bar.text = req.name  # type: ignore
        routes.append(req.get_route(maps_client))
    with alive_bar(title=f"Updating sheet {sheet_name}"):
        dicto = routes_to_dict(routes)
        frame = archiver.get_frame(sheet_name)
        new_frame = add_row_with_current_time(frame, dicto, datetime_added=forced_time)
        archiver.upload_frame(new_frame, sheet_name)


if __name__ == "__main__":
    forced_logged_datetime = datetime.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None
    with open("api_key.txt", "r", encoding="utf-8") as api:
        api_key = api.readline()
    with alive_bar(title="Connecting to Google Sheets"):
        archie = Archiver("credentials.json", "token.json", "1rc1SD6txhOa37UVoDTywIuoAxzK_7HCTEOCPeCa-Yh4")
        archie.ensure_sheets(HOME_WORK, WORK_HOME)
    with alive_bar(title="Connecting to Google Maps"):
        gmaps = googlemaps.Client(key=api_key)
    all_requests = [
        S86_A4,
        S86_DTS,
        SC_A4,
        SC_DTS,
        S1_A4,
    ]
    update_routes(
        archie,
        gmaps,
        HOME_WORK,
        all_requests,
        forced_time=forced_logged_datetime,
    )
    update_routes(
        archie,
        gmaps,
        WORK_HOME,
        all_requests,
        forced_time=forced_logged_datetime,
        reverse=True,
    )
