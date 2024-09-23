from datetime import timedelta

from implementation.location import Location


class Leg:
    def __init__(self, leg: dict) -> None:
        self.distance: float = leg["distance"]["value"] / 1000
        self.duration: timedelta
        if "duration_in_traffic" in leg:
            self.duration = timedelta(seconds=leg["duration_in_traffic"]["value"])
        else:
            self.duration = timedelta(seconds=leg["duration"]["value"])
        self.start = Location.from_node(leg, "start")
        self.end = Location.from_node(leg, "end")
        self.waypoints: list[Location] = []
        if "via_waypoint" in leg:
            self.waypoints = [Location.from_node(n) for n in leg["via_waypoint"]]
