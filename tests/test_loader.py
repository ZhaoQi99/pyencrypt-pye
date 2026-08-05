import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Tuple

import pytest

DEAFULT_META_PATH = sys.meta_path[::]


@pytest.mark.file(
    name="file1", function="test_file_1", code='\treturn "This is file test1"'
)
def test_python_file_sys_path(file_and_loader: Tuple[Path], monkeypatch):
    file_path, loader_path = file_and_loader
    monkeypatch.syspath_prepend(file_path.parent.as_posix())
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())

    sys.modules.pop("loader", None)
    sys.meta_path = DEAFULT_META_PATH.copy()

    import loader
    from file1 import test_file_1

    assert test_file_1() == "This is file test1"


@pytest.mark.license(enable=True)
@pytest.mark.file(
    name="file2", function="test_file_2", code='\treturn "This is file test2"'
)
def test_python_file_sys_path_with_license(file_and_loader: Tuple[Path], monkeypatch):
    file_path, loader_path = file_and_loader
    monkeypatch.syspath_prepend(file_path.parent.as_posix())
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())

    sys.modules.pop("loader", None)
    sys.meta_path = DEAFULT_META_PATH.copy()

    import loader
    from file2 import test_file_2

    assert test_file_2() == "This is file test2"


@pytest.mark.license(enable=True)
@pytest.mark.file(
    name="file3", function="test_file_3", code='\treturn "This is file test3"'
)
def test_python_file_sys_path_with_license_not_found(
    file_and_loader: Tuple[Path], monkeypatch
):
    file_path, loader_path = file_and_loader
    monkeypatch.syspath_prepend(file_path.parent.as_posix())
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())

    shutil.rmtree(loader_path.parent / "licenses")
    with pytest.raises(Exception) as excinfo:
        sys.modules.pop("loader", None)
        sys.meta_path = DEAFULT_META_PATH.copy()

        import loader
        from file3 import test_file_3

        assert test_file_3() == "This is file test3"

    assert str(excinfo.value) == "Could not find license file."


# Package
@pytest.mark.package(
    name="pkg1.a.b.c",
    function="test_package_1",
    code='\treturn "This is package test1"',
)
def test_python_package(package_and_loader: Tuple[Path], monkeypatch):
    package_path, loader_path = package_and_loader
    monkeypatch.syspath_prepend(package_path.as_posix())
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())

    sys.modules.pop("loader", None)
    sys.meta_path = DEAFULT_META_PATH.copy()

    import loader
    from pkg1.a.b.c import test_package_1

    assert test_package_1() == "This is package test1"


@pytest.mark.package(
    name="pkg2.a.b.c",
    function="test_package_2",
    code='\treturn "This is package test2"',
)
def test_python_package_without_init_file(package_and_loader: Tuple[Path], monkeypatch):
    package_path, loader_path = package_and_loader
    monkeypatch.syspath_prepend(package_path.as_posix())
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())

    for file in package_path.glob("**/__init__.py"):
        file.unlink()

    sys.modules.pop("loader", None)
    sys.meta_path = DEAFULT_META_PATH.copy()

    import loader
    from pkg2.a.b.c import test_package_2

    assert test_package_2() == "This is package test2"


@pytest.mark.license(enable=True)
@pytest.mark.package(
    name="pkg3.a.b.c",
    function="test_package_3",
    code='\treturn "This is package test3"',
)
def test_python_package_with_license(package_and_loader: Tuple[Path], monkeypatch):
    package_path, loader_path = package_and_loader
    monkeypatch.syspath_prepend(package_path.as_posix())
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())

    sys.modules.pop("loader", None)
    sys.meta_path = DEAFULT_META_PATH.copy()

    import loader
    from pkg3.a.b.c import test_package_3

    assert test_package_3() == "This is package test3"


@pytest.mark.license(enable=True)
@pytest.mark.package(
    name="pkg4.a.b.c",
    function="test_package_4",
    code='\treturn "This is package test4"',
)
def test_python_package_with_license_not_found(
    package_and_loader: Tuple[Path], monkeypatch
):
    package_path, loader_path = package_and_loader
    monkeypatch.syspath_prepend(package_path.as_posix())
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())

    shutil.rmtree(loader_path.parent.joinpath("licenses"))
    with pytest.raises(Exception) as excinfo:
        sys.modules.pop("loader", None)
        sys.meta_path = DEAFULT_META_PATH.copy()

        import loader
        from pkg4.a.b.c import test_package_4

        assert test_package_4() == "This is package test4"
    assert str(excinfo.value) == "Could not find license file."


_DRIVER_TEMPLATE = """\
import importlib.util, sys
{setup}
spec = importlib.util.spec_from_file_location('loader', r'{loader}')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
try:
    import secret
    print('LEAK:' + secret.VALUE)
except RuntimeError as e:
    print('BLOCKED:' + str(e))
except Exception as e:
    print('OTHER:' + type(e).__name__ + ':' + str(e))
"""


def _run_driver(work_dir, loader_path, setup):
    """在独立子进程运行驱动脚本，返回其 stdout(去除首尾空白)。"""
    script = _DRIVER_TEMPLATE.format(
        setup=textwrap.dedent(setup).strip(), loader=loader_path.as_posix()
    )
    driver = work_dir / "_driver.py"
    driver.write_text(script, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, driver.as_posix()],
        cwd=work_dir.as_posix(),
        capture_output=True,
        text=True,
    )
    return result.stdout.strip(), result.stderr.strip()


class TestAntiDebug:
    def test_clean_environment_decrypts(self, secret_and_loader):
        work_dir, loader_path, secret_value = secret_and_loader
        stdout, stderr = _run_driver(work_dir, loader_path, "pass")
        assert stdout == f"LEAK:{secret_value}", stderr

    def test_imported_debugger_is_blocked(self, secret_and_loader):
        work_dir, loader_path, _ = secret_and_loader
        setup = "import types; sys.modules['debugpy'] = types.ModuleType('debugpy')"
        stdout, stderr = _run_driver(work_dir, loader_path, setup)
        assert stdout.startswith("BLOCKED:"), stderr
        assert "not trusted" in stdout

    def test_settrace_is_blocked(self, secret_and_loader):
        work_dir, loader_path, _ = secret_and_loader
        stdout, stderr = _run_driver(
            work_dir, loader_path, "sys.settrace(lambda *a: None)"
        )
        assert stdout.startswith("BLOCKED:"), stderr
        assert "not trusted" in stdout

    def test_pdb_import_only_does_not_block(self, secret_and_loader):
        work_dir, loader_path, secret_value = secret_and_loader
        stdout, stderr = _run_driver(work_dir, loader_path, "import pdb")
        assert stdout == f"LEAK:{secret_value}", stderr
