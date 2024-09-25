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
    THROUGH_CHAR = "→"

    def __init__(
        self,
        start: str | coords,
        end: str | coords,
        waypoints: Optional[list[str | coords]] = None,
        name: Optional[str | list[str] | tuple[str]] = None,
    ) -> None:
        self.start: str | coords = start
        self.end: str | coords = end
        self.waypoints: Optional[list[str | coords]] = waypoints
        if name:
            if isinstance(name, list | tuple):
                self.name = Request.THROUGH_CHAR.join(name)
            else:
                self.name = str(name)
        else:
            self.name = None

    def reversed(self):
        reversed_waypoints = list(reversed(self.waypoints)) if self.waypoints else None
        reversed_name = self.name
        if reversed_name and Request.THROUGH_CHAR in reversed_name:
            reversed_name = Request.THROUGH_CHAR.join(reversed_name.split(Request.THROUGH_CHAR))
        return Request(
            self.end,
            self.start,
            reversed_waypoints,
            name=reversed_name
        )

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
