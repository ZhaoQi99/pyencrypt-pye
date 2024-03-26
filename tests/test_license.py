from datetime import datetime
import json
import os
import re
import shutil
from pathlib import Path

import pytest
from pyencrypt.generate import generate_aes_key
from pyencrypt.license import (
    FIELDS,
    check_license,
    generate_license_file,
    get_host_ipv4,
    get_mac_address,
)

from constants import AES_KEY


def test_get_mac_address():
    mac_address = get_mac_address()
    assert mac_address is not None
    assert (
        re.match(r"^\s*([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}\s*$", mac_address)
        is not None
    )


def test_get_host_ipv4():
    ipv4 = get_host_ipv4()
    assert ipv4 is not None
    assert re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ipv4) is not None


class TestGenerateLicense:
    def setup_method(self, method):
        self.fields = FIELDS + ["signature"]
        shutil.rmtree((Path(os.getcwd()) / "licenses").as_posix(), ignore_errors=True)

    def teardown_method(self, method):
        shutil.rmtree((Path(os.getcwd()) / "licenses").as_posix(), ignore_errors=True)

    @pytest.mark.parametrize(
        "key",
        [
            AES_KEY,
            generate_aes_key(),
        ],
    )
    def test_generate_license_file_default_path(self, key):
        license_file_path = generate_license_file(key)
        assert license_file_path.exists() is True
        license_data = json.loads(license_file_path.read_text())
        assert set(self.fields) - set(license_data.keys()) == set()
        assert license_data["mac"] is None
        assert license_data["ipv4"] is None

    @pytest.mark.parametrize(
        "key",
        [
            AES_KEY,
            generate_aes_key(),
        ],
    )
    def test_generate_license_file(self, key, tmp_path):
        license_file_path = generate_license_file(key, path=tmp_path)
        assert license_file_path.exists() is True
        license_data = json.loads(license_file_path.read_text())
        assert set(self.fields) - set(license_data.keys()) == set()
        assert license_data["mac"] is None
        assert license_data["ipv4"] is None

    @pytest.mark.parametrize(
        "key,after,before,mac_addr,ipv4",
        [
            (AES_KEY, None, None, None, None),
            (AES_KEY, None, datetime(2022, 1, 1), None, None),
            (AES_KEY, None, datetime(2022, 1, 1).astimezone(), None, None),
            (AES_KEY, datetime(2222, 1, 1), None, None, None),
            (AES_KEY, datetime(2222, 1, 1).astimezone(), None, None, None),
            (AES_KEY, None, None, get_mac_address(), None),
            (AES_KEY, None, None, None, get_host_ipv4()),
        ],
    )
    def test_check_license(self, key, after, before, mac_addr, ipv4, tmp_path):
        license_file_path = generate_license_file(
            key, path=tmp_path, after=after, before=before, mac_addr=mac_addr, ipv4=ipv4
        )
        assert check_license(license_file_path, key) is True

    @pytest.mark.parametrize(
        "key",
        [
            AES_KEY,
            generate_aes_key(),
        ],
    )
    def test_check_license_invalid(self, key, tmp_path):
        license_file_path = generate_license_file(key, path=tmp_path)
        license_data = json.loads(license_file_path.read_text())
        license_data["signature"] = "invalid"
        license_file_path.write_text(json.dumps(license_data), encoding="utf-8")
        with pytest.raises(Exception) as excinfo:
            check_license(license_file_path, key)
        assert str(excinfo.value) == "License signature is invalid."

    @pytest.mark.parametrize(
        "key,after,before",
        [
            (AES_KEY, datetime(2000, 1, 1), None),
            (generate_aes_key(), datetime(2000, 1, 1), None),
            (AES_KEY, None, datetime(2222, 1, 1)),
            (generate_aes_key(), None, datetime(2222, 1, 1)),
        ],
    )
    def test_check_license_expired(self, key, after, before, tmp_path):
        license_file_path = generate_license_file(
            key, path=tmp_path, after=after, before=before
        )
        with pytest.raises(Exception) as excinfo:
            check_license(license_file_path, key)
        assert str(excinfo.value) == "License expired."

    @pytest.mark.parametrize(
        "key,mac_addr",
        [
            (AES_KEY, "invalid mac address"),
            (generate_aes_key(), "invalid mac address"),
        ],
    )
    def test_check_license_mac_addr(self, key, mac_addr, tmp_path):
        license_file_path = generate_license_file(key, path=tmp_path, mac_addr=mac_addr)
        with pytest.raises(Exception) as excinfo:
            check_license(license_file_path, key)
        assert str(excinfo.value) == "Machine mac address is invalid."

    @pytest.mark.parametrize(
        "key,ipv4",
        [
            (AES_KEY, "invalid ipv4 address"),
            (generate_aes_key(), "invalid ipv4 address"),
        ],
    )
    def test_check_license_ipv4(self, key, ipv4, tmp_path):
        license_file_path = generate_license_file(key, path=tmp_path, ipv4=ipv4)
        with pytest.raises(Exception) as excinfo:
            check_license(license_file_path, key)
        assert str(excinfo.value) == "Machine ipv4 address is invalid."
