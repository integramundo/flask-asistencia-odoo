from flask import Flask, request
from odoo_post_attendance import post_attendance
from odoo_get_attendance import get_attendance

app = Flask(__name__)


@app.route("/hello/<name>", methods=["GET"])
def hello_name(name):
    return f"Hello {name}"


@app.route("/get_attendance", methods=["GET"])
def get_attendance_route():
    file_path = request.args.get("file_path")
    username = request.args.get("username")
    verbose = request.args.get("verbose")

    if verbose and verbose.lower() in ["true", "1"]:
        verbose = True
    else:
        verbose = False

    result = get_attendance(file_path, username, verbose)
    return result


@app.route("/post_attendance", methods=["GET"])
def post_attendance_route():
    file_path = request.args.get("file_path")
    action = request.args.get("action")
    username = request.args.get("username")
    verbose = request.args.get("verbose")

    if verbose and verbose.lower() in ["true", "1"]:
        verbose = True
    else:
        verbose = False

    result = post_attendance(file_path, action, username, verbose)
    return result


if __name__ == "__main__":
    app.run(debug=True)
