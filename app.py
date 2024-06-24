from flask import Flask, request
from odoo_post_attendance import post_attendance
from odoo_get_attendance import get_attendance
import os
import json

# Assuming the users.json file is in the same directory as your main application file
user_mapping_path = os.path.join(os.path.dirname(__file__), "users.json")

# Check if the file exists at the defined path
if not os.path.isfile(user_mapping_path):
    raise ValueError(f"User mapping file not found at {user_mapping_path}")

# Load the username mapping data from the file
with open(user_mapping_path) as f:
    user_map = json.load(f)


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

    # Map username to real name if it exists
    real_name = user_map.get(username)
    if not real_name:
        return f"Error: Username '{username}' not found in mapping.", 404

    result = get_attendance(file_path, real_name, verbose)
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

    # Map username to real name if it exists
    real_name = user_map.get(username)
    if not real_name:
        return f"Error: Username '{username}' not found in mapping.", 404

    result = post_attendance(file_path, action, real_name, verbose)
    return result


if __name__ == "__main__":
    app.run(debug=True)
