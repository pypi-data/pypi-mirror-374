# Standard Libraries
from datetime import datetime


class SingleITMetadata:
    def __init__(self, raw_metadata: dict[str, int]):
        self.CAMERA = raw_metadata.get("CAMERA")
        self.DATETIME = datetime(
            raw_metadata["YEAR"],
            raw_metadata["MONTH"],
            raw_metadata["DAY"],
            raw_metadata["HOUR"],
            raw_metadata["MINUTE"],
            raw_metadata["SECOND"],
            raw_metadata["DECIMAL"],
        ).strftime("%Y-%m-%d_%H:%H:%S.%f")
        self.INTTIME = raw_metadata.get("IT")
