import pytest
from pyencrypt.encrypt import encrypt_file, encrypt_key, generate_so_file
from pyencrypt.generate import generate_aes_key
from pyencrypt.license import generate_license_file


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "file(name,function,code): mark test to run only on named environment",
    )
    config.addinivalue_line(
        "markers", "license(enable,kwargs): mark test to run only on named environment"
    )
    config.addinivalue_line(
        "markers",
        "package(name,function,code): mark test to run only on named environment",
    )


@pytest.fixture(scope="function")
def file_and_loader(request, tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("file")

    file_marker = request.node.get_closest_marker("file")
    file_name = file_marker.kwargs.get("name")
    function_name = file_marker.kwargs.get("function")
    code = file_marker.kwargs.get("code")

    license_marker = request.node.get_closest_marker("license")
    license, kwargs = False, {}
    if license_marker is not None:
        kwargs = license_marker.kwargs
        license = kwargs.pop("enable", True)

    file_path = tmp_path / f"{file_name}.py"
    file_path.touch()
    file_path.write_text(
        """\
def {function_name}():
{code}
    """.format(
            function_name=function_name, code=code
        ),
        encoding="utf-8",
    )
    # generate loader.so
    key = generate_aes_key()
    new_path = file_path.with_suffix(".pye")
    encrypt_file(file_path, key, new_path=new_path)
    file_path.unlink()
    cipher_key, d, n = encrypt_key(key)
    loader_path = generate_so_file(cipher_key, d, n, file_path.parent, license=license)
    work_dir = loader_path.parent
    work_dir.joinpath("loader.py").unlink()
    work_dir.joinpath("loader.c").unlink()
    work_dir.joinpath("loader_origin.py").unlink()

    # License
    license and generate_license_file(key.decode(), work_dir, **kwargs)
    generate_license_file(key.decode(), work_dir)
    return (new_path, loader_path)


@pytest.fixture(scope="function")
def package_and_loader(request, tmp_path_factory):
    pkg_path = tmp_path_factory.mktemp("package")

    file_marker = request.node.get_closest_marker("package")
    package_name = file_marker.kwargs.get("name")
    function_name = file_marker.kwargs.get("function")
    code = file_marker.kwargs.get("code")

    license_marker = request.node.get_closest_marker("license")
    license, kwargs = False, {}
    if license_marker is not None:
        kwargs = license_marker.kwargs
        license = kwargs.pop("enable", True)

    current = pkg_path
    for dir_name in package_name.split(".")[:-1]:
        current = current.joinpath(dir_name)
        current.mkdir()
        current.joinpath("__init__.py").touch()

    file_path = current.joinpath(f'{package_name.split(".")[-1]}.py')
    file_path.write_text(
        """\
def {function_name}():
{code}
    """.format(
            function_name=function_name, code=code
        ),
        encoding="utf-8",
    )

    new_path = file_path.with_suffix(".pye")
    key = generate_aes_key()
    encrypt_file(file_path, key, new_path=new_path)
    file_path.unlink()

    cipher_key, d, n = encrypt_key(key)
    loader_path = generate_so_file(cipher_key, d, n, pkg_path, license)
    work_dir = loader_path.parent
    work_dir.joinpath("loader.py").unlink()
    work_dir.joinpath("loader.c").unlink()
    work_dir.joinpath("loader_origin.py").unlink()
    # License
    license and generate_license_file(key.decode(), work_dir, **kwargs)
    return pkg_path, loader_path
