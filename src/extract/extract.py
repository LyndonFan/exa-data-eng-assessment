import os
from datetime import datetime, timezone
import orjson
from pathlib import Path
from typing import Any

from fsspec.implementations.local import LocalFileSystem
# from gcsfs import GCSFileSystem
from fhir.resources.R4B.bundle import Bundle, BundleEntry

from dotenv import load_dotenv

load_dotenv()

class Extractor:
    def __init__(self, filesystem: str = "local"):
        self.bucket = os.environ["BUCKET"]
        self.filesystem = filesystem
        if filesystem == "local":
            self.fs = LocalFileSystem(True)
        # elif filesystem == "google":
        #     self.fs = GCSFileSystem()
        else:
            raise ValueError(f"Unsupported filesystem: {filesystem}")

    def save_raw_file(self, data: dict[str, Any], original_path: Path):
        time_now = datetime.now(timezone.utc)
        # not use ":" as windows or other file systems may think it's special
        upload_time_string = time_now.isoformat(timespec="seconds").replace(":", "-")
        new_base_name = f"{original_path.stem}_{upload_time_string}.json"
        new_path = Path(self.bucket) / f"upload_date={time_now.strftime('%Y-%m-%d')}" / new_base_name
        with self.fs.open(new_path, "w") as f:
            f.write(orjson.dumps(data).decode("utf-8"))

    def extract(self, payload_path: str | Path) -> list[BundleEntry]:
        with self.fs.open(payload_path, "rb") as f:
            data = orjson.loads(f.read())
        self.save_raw_file(data, Path(payload_path))
        bundle = Bundle.parse_obj(data)
        if bundle.type != "transaction":
            raise ValueError(f"Expected transaction bundle, got {bundle.type}")
        if bundle.entry is None:
            raise ValueError(f"Expected bundle entry, got {bundle.entry}")
        return bundle.entry # type: ignore