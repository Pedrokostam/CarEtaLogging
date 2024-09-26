from implementation.request import Request, RequestPackage
from implementation import coords

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
FASTEST = Request(
    **endpoints,
    waypoints=None,
    name="Fastest",
)

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

REQUEST_PACKAGE = RequestPackage(
    ["Dom", "Praca"],
    FASTEST,
    S86_A4,
    S86_DTS,
    SC_A4,
    SC_DTS,
    S1_A4,
)
