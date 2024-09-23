from datetime import datetime
from typing import Optional

import googlemaps
from googlemaps.directions import directions
from implementation import coords
from implementation.route import Route


def to_via(point: str | coords):
    if isinstance(point, str):
        return f"via:{point}"
    if isinstance(point, tuple):
        return f"via:{point[0]},{point[1]}"
    raise ValueError("Incorrect point format")


class Request:
    def __init__(
        self,
        start: str | coords,
        end: str | coords,
        waypoints: Optional[list[str | coords]] = None,
        name: Optional[str] = None,
    ) -> None:
        self.start: str | coords = start
        self.end: str | coords = end
        self.waypoints: Optional[list[str | coords]] = waypoints
        self.name = name

    def reversed(self):
        reversed_waypoints = list(reversed(self.waypoints)) if self.waypoints else None
        return Request(self.end, self.start, reversed_waypoints)

    def get_route(self, client: googlemaps.Client):
        vias = [to_via(x) for x in self.waypoints] if self.waypoints else None
        node = directions(
            client=client,
            origin=self.start,
            destination=self.end,
            waypoints=vias,
            departure_time=datetime.now(),
        )
        return Route(node[0], custom_name=self.name)
