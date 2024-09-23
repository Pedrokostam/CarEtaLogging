from operator import attrgetter
import googlemaps
from implementation.request import Request

home = (50.30442699863767, 19.183934458803197)
work = (50.27773270036598, 18.687399321484765)
IKEA = (50.26649709372005, 19.05295016568546)
SC = (50.26780188191576, 19.109929286643524)

FASTEST = Request(
    home,
    work,
)

endpoints = {"start": home, "end": work}

DK94_A4 = Request(
    **endpoints,
    waypoints=[
        IKEA,
        (50.2463085928673, 19.022898282245237),
    ],
    name="DK94-A4",
)
SC_A4 = Request(
    **endpoints,
    waypoints=[
        SC,
        (50.2463085928673, 19.022898282245237),
    ],
    name="DK94-A4",
)
DK94_DTS = Request(
    **endpoints,
    waypoints=[
        IKEA,
        (50.27057254692684, 18.997468954488145),
    ],
    name="DK94-DTS",
)
SC_DTS = Request(
    **endpoints,
    waypoints=[
        SC,
        (50.27057254692684, 18.997468954488145),
    ],
    name="DK94-DTS",
)

S1_A4 = Request(
    **endpoints,
    waypoints=[(50.216042902454475, 19.170816378726194)],
    name="S1-A4",
)


if __name__ == "__main__":
    with open('api_key.txt','r',encoding='utf-8') as api:
        api_key = api.readline()
    gmaps = googlemaps.Client(key=api_key)
    arr = [
        #FASTEST,
        SC_A4,
        DK94_A4,
        DK94_DTS,
        SC_DTS,
        S1_A4,
    ]
    to_work = [a.get_route(gmaps) for a in arr]
    best_to_work =min(to_work,key=attrgetter('duration'))
    to_home = [a.reversed().get_route(gmaps) for a in arr]
    best_to_home =min(to_home,key=attrgetter('duration'))
    print(best_to_work)
    print(best_to_home)
