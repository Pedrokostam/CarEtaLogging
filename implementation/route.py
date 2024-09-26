import json
from datetime import timedelta
from typing import Optional

from implementation.leg import Leg


class Route:
    def __init__(self, route_dict: dict, custom_name: Optional[str] = None):
        self.summary = route_dict["summary"]
        self.name = custom_name or self.summary
        self.legs = [Leg(d) for d in route_dict["legs"]]
        self.start = self.legs[0].start
        self.end = self.legs[-1].end
        self.duration = timedelta(seconds=sum(l.duration.seconds for l in self.legs))
        self.distance = sum(l.distance for l in self.legs)

    def __repr__(self):
        d = {
            "summary": self.summary,
            "name": self.name,
            # "legs": self.legs,
            "start": str(self.start),
            "end": str(self.end),
            "duration": str(self.duration),
            "distance": f"{self.distance}km",
        }
        return json.dumps(d, indent=2, ensure_ascii=False)
