from pathlib import Path
import sys
import shutil
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
