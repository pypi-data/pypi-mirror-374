""" "Service for interacting with the FIL SFTP server."""

import json
import subprocess
from datetime import UTC, datetime
from gzip import GzipFile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Self

import xmltodict

# from sftpretty import Connection
from avwx_swift.notam import Notam

DATE_FILE = "primary_last_date.txt"
# TIME_FORMAT = "%Y-%m-%d %H:%M:%S %Z"
FIL_FILE_NAME = "initial_load_aixm.xml.gz"
JSON_FILE_NAME = "filservice.json"


def _load_dt(value: str | None) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


_NAMESPACES = (
    "http://www.w3.org/2001/XMLSchema-instance",
    "http://www.w3.org/1999/xhtml",
    "http://www.opengis.net/ows/1.1",
    "http://www.isotc211.org/2005/gts",
    "http://www.aixm.aero/schema/5.1/event",
    "urn:us.gov.dot.faa.aim.fns",
    "http://www.aixm.aero/schema/5.1/message",
    "http://www.opengis.net/wfs-util/2.0",
    "http://www.w3.org/1999/xlink",
    "http://www.opengis.net/wfs/2.0",
    "http://www.opengis.net/fes/2.0",
    "http://www.opengis.net/gml/3.2",
    "http://www.aixm.aero/schema/5.1/extensions/FAA/FNSE",
    "http://www.isotc211.org/2005/gco",
    "http://www.isotc211.org/2005/gmd",
    "http://www.aixm.aero/schema/5.1",
)
_NS_MAP = {ns: None for ns in _NAMESPACES}


class FilService:
    """Service for interacting with the FIL SFTP server."""

    url: str
    user: str
    cert_path: Path
    cache_dir: Path | None = None

    data: list[Notam]

    checked: datetime | None = None
    updated: datetime | None = None
    server_time: datetime | None = None

    def __init__(self, url: str, user: str, cert_path: Path, cache_dir: Path | None = None) -> None:
        if cache_dir and not cache_dir.exists():
            cache_dir.mkdir(parents=True)
        self.url = url
        self.user = user
        self.cert_path = cert_path
        self.cache_dir = cache_dir
        self.data = []

    def __repr__(self) -> str:
        return f"FilService(size={len(self.data)}, checked={self.checked}, updated={self.updated}, server_time={self.server_time})"

    def save_cache(self) -> None:
        """Save the current state to the cache directory."""
        if self.cache_dir is None:
            msg = "Cache directory is not set."
            raise ValueError(msg)
        attrs = {
            "url": self.url,
            "user": self.user,
            "cert_path": self.cert_path.as_posix(),
            "cache_dir": self.cache_dir.as_posix(),
            "checked": self.checked.isoformat() if self.checked else None,
            # "updated": self.updated.isoformat() if self.updated else None,
            "server_time": self.server_time.isoformat() if self.server_time else None,
        }
        cache_file = self.cache_dir / JSON_FILE_NAME
        with cache_file.open("w") as fout:
            json.dump(attrs, fout)

    def update(self, *, force: bool = False) -> bool:
        """Update the local cache with the latest data from the SFTP server."""

        # NOTE: The OpenSSH key provided by FAA SWIFT is apparently malformed though still works.
        # It fails sftpretty's pubkey validation steps as it is an RSA key masquerading as ED25519
        # I'm keeping this line here for future reference in case this is ever fixed. The original
        # flow was to pass this connection through the update steps. The CMD sftp still works.

        # with Connection(self.url, username=self.user, private_key=self.cert_path.as_posix()) as sftp:

        if self.cache_dir is None:
            with TemporaryDirectory() as tmpdir:
                return self._update(Path(tmpdir), force=force)
        else:
            return self._update(self.cache_dir, force=force)

    @property
    def should_update(self) -> bool:
        """Determine if an update is needed based on server time."""
        if not self.server_time:
            msg = "Server time has not been fetched."
            raise ValueError(msg)
        if not self.updated:
            return True
        return self.updated < self.server_time

    def _update(self, target_dir: Path, *, force: bool) -> bool:
        """Update the local cache with the latest data from the SFTP server."""
        self.update_server_time(target_dir)
        if not (force or self.should_update):
            return False
        self._download(target_dir)
        self._parse(target_dir)
        if self.cache_dir:
            self.save_cache()
        return True

    def _get_file(self, name: str, target: Path) -> None:
        """Download a file from the SFTP server using the command line."""
        cmd = ["sftp", "-i", str(self.cert_path), f"{self.user}@{self.url}:{name}", str(target)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            msg = f"SFTP failed: {result.stderr}"
            raise RuntimeError(msg)

    def update_server_time(self, target_dir: Path) -> datetime:
        """Fetch and return the most recent update time from the SFTP server."""
        path = target_dir / DATE_FILE
        self._get_file(DATE_FILE, path)
        with path.open() as fin:
            self.server_time = datetime.fromisoformat(fin.read().strip()).replace(tzinfo=UTC)
        self.checked = datetime.now(UTC)
        return self.server_time

    def _download(self, target_dir: Path) -> None:
        """Download the FIL file from the SFTP server."""
        path = target_dir / FIL_FILE_NAME
        self._get_file(FIL_FILE_NAME, path)

    def _parse(self, target_dir: Path) -> None:
        """Parse the FIL file and extract NOTAMs."""
        self.data = []
        path = target_dir / FIL_FILE_NAME

        def parse_notam(_: Any, item: dict[str, Any]) -> bool:
            self.data.append(Notam.from_fil(item))
            return True  # Indicates that the parser should continue

        xmltodict.parse(
            GzipFile(path),
            item_depth=5,
            item_callback=parse_notam,
            process_namespaces=True,
            namespaces=_NS_MAP,
        )

        self.updated = datetime.now(UTC)

    @classmethod
    def from_cache(cls, cache_dir: Path, *, load_data: bool = True) -> Self:
        """Load the FIL service instance from the cache directory."""
        if not cache_dir.exists():
            msg = "Cache directory does not exist."
            raise ValueError(msg)
        cache_file = cache_dir / JSON_FILE_NAME
        with cache_file.open() as fin:
            attrs = json.load(fin)
        obj = cls(
            url=attrs["url"],
            user=attrs["user"],
            cert_path=Path(attrs["cert_path"]),
            cache_dir=Path(attrs["cache_dir"]),
        )
        obj.checked = _load_dt(attrs["checked"])
        obj.server_time = _load_dt(attrs["server_time"])
        if load_data:
            obj._parse(cache_dir)  # noqa
        return obj
