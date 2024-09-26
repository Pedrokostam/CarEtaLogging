from alive_progress import alive_bar, config_handler
import googlemaps


coords = tuple[float, float]


class Configuration:
    def __init__(self) -> None:
        self.upload = True


CONFIG = Configuration()


config_handler.set_global(
    monitor=False,
    elapsed="{elapsed}",
    elapsed_end="(took {elapsed})",
    spinner_length=5,
    bar=None,
    stats=False,
    stats_end=False,
)


def get_map_client(api_key: str) -> googlemaps.Client:
    with alive_bar(title="Connecting to Google Maps"):
        return googlemaps.Client(key=api_key)
