from flask import Flask, request
from odoo_post_attendance import post_attendance
from odoo_get_attendance import get_attendance

# Dictionary mapping usernames to real names
user_map = {
    "User 1": "Cristopher Ferrada",
    "User 2": "Ariela Ferrada Calbún",
    "User 3": "Nicolás Hernández Díaz",
    "User 4": "Larissa Farfán",
    "User 5": "Lissette Navarrete",
    "User 6": "Alejandra Paillas",
    "User 7": "Carolina Díaz",
    "User 8": "Leonardo Ferrada Vilches",
    "User 9": "German Tapia",
    "User 10": "Rodrigo Bicirra",
    # Add more mappings here as needed
}

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
