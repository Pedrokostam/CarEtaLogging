from datetime import datetime
from operator import attrgetter
from typing import Optional

from alive_progress import alive_bar, alive_it
import googlemaps
from googlemaps.directions import directions
import googlemaps.roads
from implementation import CONFIG, coords
from implementation.archiver import Archiver, add_row_with_current_time, routes_to_dict
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
        self._name: Optional[list[str]] = None
        if name:
            if isinstance(name, list | tuple):
                self._name = list(name)
            else:
                self._name = [name]

    @property
    def name(self):
        if self._name:
            return Request.THROUGH_CHAR.join(self._name)
        return None

    def reversed(self):
        reversed_waypoints = list(reversed(self.waypoints)) if self.waypoints else None
        reversed_name = self.name
        if reversed_name and Request.THROUGH_CHAR in reversed_name:
            parts = reversed_name.split(Request.THROUGH_CHAR)
            reversed_parts = reversed(parts)
            reversed_name = Request.THROUGH_CHAR.join(reversed_parts)
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
        nodes = directions(client=client, departure_time=depart_time, alternatives=True, **params)
        routes = [Route(n, custom_name=self.name) for n in nodes]
        fastest_route = min(routes, key=attrgetter("duration"))
        return fastest_route


class RequestPackage:
    def __init__(self, first_direction_endpoint_names: list[str] | tuple[str], *requests: Request) -> None:
        assert first_direction_endpoint_names
        assert requests
        self._endpoint_names = list(first_direction_endpoint_names)
        self._requests = list(requests)

    @property
    def first_direction_sheet_name(
        self,
    ):
        return Request.THROUGH_CHAR.join(self._endpoint_names)

    @property
    def requests(self):
        return self._requests

    @property
    def reversed_requests(self):
        return [x.reversed() for x in self._requests]

    @property
    def reversed_direction_sheet_name(
        self,
    ):
        return Request.THROUGH_CHAR.join(reversed(self._endpoint_names))

    @property
    def sheet_names(self):
        return [self.first_direction_sheet_name, self.reversed_direction_sheet_name]

    def get_request_list(self, reverse: bool):
        if reverse:
            return self.requests
        return self.reversed_requests

    def get_sheetname(self, reverse: bool):
        if reverse:
            return self.first_direction_sheet_name
        return self.reversed_direction_sheet_name

    def update_routes(
        self,
        archiver: Archiver,
        maps_client: googlemaps.Client,
        *,
        reverse: bool = False,
        forced_log_time: Optional[datetime] = None,
        forced_departure_time: Optional[datetime] = None,
    ):
        sheet_name = self.get_sheetname(reverse)
        p_bar = alive_it(
            self.get_request_list(reverse),
            title=f"Getting routes for {sheet_name}",
        )
        routes = []
        for req in p_bar:
            p_bar.text = req.name  # type: ignore
            routes.append(req.get_route(maps_client, forced_departure_time))
        with alive_bar(title=f"Updating sheet {sheet_name}"):
            dicto = routes_to_dict(routes)
            frame = archiver.get_frame(sheet_name)
            new_frame = add_row_with_current_time(frame, dicto, datetime_added=forced_log_time)
            if CONFIG.upload:
                archiver.upload_frame(new_frame, sheet_name)
