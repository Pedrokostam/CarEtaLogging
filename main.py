from datetime import datetime
from implementation import get_map_client
from implementation.archiver import Archiver
from implementation.arguments import parse_arguments
from requested_routes import REQUEST_PACKAGE

if __name__ == "__main__":
    args = parse_arguments()
    archie = Archiver.initialize(args.sheet_id, REQUEST_PACKAGE.sheet_names)
    gmaps = get_map_client(args.api_key)
    params = {
        "archiver": archie,
        "maps_client": gmaps,
        "forced_departure_time": datetime.now(),
        "forced_log_time": args.log_date,
    }
    REQUEST_PACKAGE.update_routes(**params, reverse=False)
    REQUEST_PACKAGE.update_routes(**params, reverse=True)
