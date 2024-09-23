from typing import cast
from implementation import coords


class Location:
    def __init__(self, address: str, coordinates: coords) -> None:
        self.address = address
        self.coordinates = coordinates

    @classmethod
    def from_node(cls, node: dict, prefix: str = ""):
        prefix = prefix.strip() if prefix else ""
        address_key_name = f"{prefix}_address" if prefix else "address"
        location_key_name = f"{prefix}_location" if prefix else "location"
        if address_key_name in node:
            address = cast(str, node[address_key_name])
        else:
            address = ""
        if location_key_name in node:
            location = (node[location_key_name]["lat"], node[location_key_name]["lng"])
        else:
            location = (0, 0)
        return Location(address, location)

    def __repr__(self):
        return self.address or self.coordinates
