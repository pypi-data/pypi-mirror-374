from __future__ import annotations

from flask import abort
from flask import Blueprint
from flask import Flask
from flask import get_template_attribute
from flask import render_template
from flask import request

from .explorer import find_directory_from_request
from .explorer import get_mountpoints
from .explorer import init_mountpoints

exp = Blueprint("explorer", __name__, template_folder="templates")


@exp.route("/change_directory")
def change_directory() -> str:
    mountpoints = get_mountpoints()
    explorer = find_directory_from_request(mountpoints)
    if explorer is None:
        abort(404)

    texplorer = get_template_attribute("explorer.html", "explorer")
    return texplorer(mountpoints, explorer)  # type: ignore


# @exp.route("/change_directory_json")
# def change_directory_json() -> Response:  # pragma: no cover
#     # pragma: no cover
#     mountpoints = get_mountpoints()
#     explorer = find_directory_from_request(mountpoints)
#     if explorer is None:
#         return error_resp("unknown directory", 404)
#     return jsonify(
#         dict(
#             explorer=explorer.tojson(),
#             mountpoints=[m.label for m in mountpoints.mountpoints],
#         ),
#     )


def test() -> None:
    @exp.route("/explorer-test.html")
    def explorer_test() -> str:  # pragma: no cover

        mountpoint = request.values.get("mountpoint", "HOME")

        mountpoints = get_mountpoints()
        mp = mountpoints.get(mountpoint)
        if mp is None:
            mp = mountpoints.mountpoints[0]

        explorer = mp.home()
        if explorer is None:
            abort(404)
        return render_template(
            "explorer-test.html",
            explorer=explorer,
            mountpoints=mountpoints,
            eid="explorer",
        )


def init_app(app: Flask, url_prefix: str = "/") -> None:

    init_mountpoints(app)

    if app.debug:  # pragma: no cover
        test()
    app.register_blueprint(exp, url_prefix=url_prefix)
