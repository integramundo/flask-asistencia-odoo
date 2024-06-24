from flask import Flask, request, jsonify
from odoo_post_attendance import post_attendance
from odoo_get_attendance import get_attendance
import os

# Assuming the users.txt file is in the same directory as your main application file
user_mapping_path = os.path.join(os.path.dirname(__file__), "users.txt")

# Check if the file exists at the defined path
if not os.path.isfile(user_mapping_path):
    raise ValueError(f"User mapping file not found at {user_mapping_path}")

# Load the username mapping data from the file
user_map = {}
with open(user_mapping_path) as f:
    for line in f:
        line = line.strip()
        if line:
            username, real_name = line.split("=", 1)
            user_map[username.strip()] = real_name.strip()

app = Flask(__name__)


@app.route("/hello/<name>", methods=["GET"])
def hello_name(name):
    return f"Hello {name}\n"


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
        return (
            jsonify(
                {
                    "message": f"Error: Username '{username}' not found in mapping.",
                    "status_code": 404,
                }
            ),
            404,
        )

    result = get_attendance(file_path, real_name, verbose)
    return jsonify(result)


@app.route("/post_attendance", methods=["POST"])
def handle_attendance():
    # Get the JSON data from the request
    try:
        data = request.get_json()
    except Exception as e:
        return (
            jsonify({"message": f"Error parsing JSON data: {e}", "status_code": 400}),
            400,
        )

    # Ensure required fields are present
    required_fields = ["file_path", "action", "username"]
    for field in required_fields:
        if field not in data:
            return (
                jsonify({"message": f"Missing field: {field}", "status_code": 400}),
                400,
            )

    # Extract relevant information from the JSON
    file_path = data.get("file_path")
    action = data.get("action")
    username = data.get("username")
    verbose = data.get("verbose", False)  # Default verbose to False

    # Map username to real name if it exists
    real_name = user_map.get(username)
    if not real_name:
        return (
            jsonify(
                {
                    "message": f"Error: Username '{username}' not found in mapping.",
                    "status_code": 404,
                }
            ),
            404,
        )

    # Process attendance data
    result, status_code = post_attendance(file_path, action, real_name, verbose)

    # Ensure the response from post_attendance is a dictionary
    if isinstance(result, dict):
        return jsonify(result), status_code
    else:
        return jsonify({"message": "Unexpected error.", "status_code": 500}), 500


if __name__ == "__main__":
    app.run(debug=True)
