import hashlib
import json
import os
import socket
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

from pyencrypt.aes import aes_encrypt

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
MIN_DATETIME = datetime.now().astimezone()
MAX_DATETIME = datetime(year=2999, month=12, day=31).astimezone()


def get_mac_address() -> str:
    return ":".join(("%012X" % uuid.getnode())[i : i + 2] for i in range(0, 12, 2))


def get_host_ipv4() -> str:
    if sys.platform == "darwin":
        command = "ifconfig | grep 'inet ' | grep -Fv 127.0.0.1 | awk '{print $2}'"
        return subprocess.check_output(command, shell=True).decode().split()[-1]
    else:
        return socket.gethostbyname(socket.gethostname())


def get_signature(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


FIELDS = ["invalid_before", "invalid_after", "ipv4", "mac"]


def _combine_data(data: dict) -> bytes:
    return "*".join(map(lambda x: f"{x}:{data[x]}", FIELDS)).encode()  # noqa: E231


def generate_license_file(
    aes_key: str,
    path: Path = None,
    after: datetime = None,
    before: datetime = None,
    mac_addr: str = None,
    ipv4: str = None,
    **extra,
):
    if after is None:
        after = MAX_DATETIME
    if before is None:
        before = MIN_DATETIME

    if after.tzinfo is None:
        after = after.astimezone()
    if before.tzinfo is None:
        before = before.astimezone()

    data = {
        "invalid_before": before.strftime(DATE_FORMAT),
        "invalid_after": after.strftime(DATE_FORMAT),
        "mac": mac_addr,
        "ipv4": ipv4,
    }
    encrypted_data = aes_encrypt(_combine_data(data), aes_key)
    signature = get_signature(encrypted_data)
    data.update({"signature": signature, **extra})

    if path is None:
        path = Path(os.getcwd())
    license_dir = path / "licenses"
    license_dir.mkdir(exist_ok=True)
    license_path = license_dir / "license.lic"
    license_path.touch(exist_ok=True)
    license_path.write_bytes(json.dumps(data, indent=4).encode())
    return license_path.absolute()


def check_license(license_path: Path, aes_key: str):
    if not license_path.exists():
        raise FileNotFoundError(
            f"License file {license_path.absolute().as_posix()} not found."
        )
    data = json.loads(license_path.read_text())
    signature = data.pop("signature")
    before = datetime.strptime(data["invalid_before"], DATE_FORMAT).astimezone()
    after = datetime.strptime(data["invalid_after"], DATE_FORMAT).astimezone()
    mac_address = data.get("mac")
    ipv4 = data.get("ipv4")
    now = datetime.now().astimezone()
    if signature != get_signature(aes_encrypt(_combine_data(data), aes_key)):
        raise Exception("License signature is invalid.")
    if now < before or now > after:
        raise Exception("License expired.")
    if mac_address and mac_address != get_mac_address():
        raise Exception("Machine mac address is invalid.")
    if ipv4 and ipv4 != get_host_ipv4():
        raise Exception("Machine ipv4 address is invalid.")
    return True
