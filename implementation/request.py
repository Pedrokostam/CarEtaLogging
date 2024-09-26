from datetime import datetime
import json
from typing import Optional

import googlemaps
from googlemaps.directions import directions
import googlemaps.roads
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
        return Request(self.end, self.start, reversed_waypoints, name=reversed_name)

    def get_interpolated_params(self, client: googlemaps.Client):
        all_waypoints = self.waypoints or []
        all_waypoints.insert(0, self.start)
        all_waypoints.append(self.end)
        interpolated_result = googlemaps.roads.snap_to_roads(client, all_waypoints, interpolate=True)
        interpolated_coords = [(p["location"]["latitude"], p["location"]["longitude"]) for p in interpolated_result]
        inter_start = interpolated_coords[0]
        inter_end = interpolated_coords[-1]
        inter_waypoints = interpolated_coords[1:-1]
        inter_via = [to_via(wp) for wp in inter_waypoints]
        return {
            "origin": inter_start,
            "destination": inter_end,
            "waypoints": inter_via,
        }

    def get_route(self, client: googlemaps.Client, depart_time: Optional[datetime] = None):
        params = self.get_interpolated_params(client)
        depart_time = depart_time or datetime.now()
        node = directions(client=client, departure_time=depart_time, **params)
        return Route(node[0], custom_name=self.name)
