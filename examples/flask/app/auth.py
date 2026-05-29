from functools import wraps

from flask import Blueprint, jsonify, request

bp = Blueprint("auth", __name__, url_prefix="/account")


def _check_license() -> str | None:
    try:
        import loader

        file_loader = loader.EncryptFileLoader("")
        if file_loader.license is True:
            file_loader.check()
    except ModuleNotFoundError:
        return None
    except Exception as exc:
        return str(exc)
    return None


def check_license(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        error = _check_license()
        if error:
            return jsonify({"message": error}), 403
        return view(*args, **kwargs)

    return wrapper


@bp.get("/login/")
@check_license
def login():
    username = request.args.get("username", "")
    password = request.args.get("password", "")
    if username == "admin" and password == "admin":
        return jsonify({"message": "ok"})
    return jsonify({"message": "invalid credentials"}), 401
