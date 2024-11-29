import sys
from pathlib import Path
from typing import Tuple

import pytest

CODE1 = """
    try:
        a = 1/0
    except Exception as e:
        import traceback
        return traceback.format_exc()
def fun():
    return _fun()
"""


@pytest.mark.file(name="file_trace1", function="_fun", code=CODE1)
def test_traceback_format_exc(file_and_loader: Tuple[Path], monkeypatch):
    file_path, loader_path = file_and_loader
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())
    monkeypatch.syspath_prepend(file_path.parent.as_posix())

    sys.modules.pop("loader", None)

    import loader
    from file_trace1 import fun

    msg = None
    try:
        msg = fun()
    except Exception:
        pass
    if not msg:
        pytest.fail("`format_exc` return None")


CODE2 = """
    try:
        a = 1/0
    except Exception as e:
        import traceback
        traceback.print_stack()
def _fun2():
    _fun()
def _fun3():
    _fun2()

def fun2():
    _fun3()
"""


@pytest.mark.file(name="file_trace2", function="_fun", code=CODE2)
def test_traceback_print_stack(file_and_loader: Tuple[Path], monkeypatch, capsys):
    file_path, loader_path = file_and_loader
    monkeypatch.syspath_prepend(loader_path.parent.as_posix())
    monkeypatch.syspath_prepend(file_path.parent.as_posix())

    sys.modules.pop("loader", None)

    import loader
    from file_trace2 import fun2

    try:
        fun2()
    except Exception:
        pass

    captured = capsys.readouterr()
    out = captured.err

    assert "in fun" in out
    assert "in _fun3" in out
    assert "in _fun2" in out
    assert "in _fun" in out
