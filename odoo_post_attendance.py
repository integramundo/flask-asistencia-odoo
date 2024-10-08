import xmlrpc.client
import re
import sys
from datetime import datetime, timezone
from flask import Flask, request, jsonify


# Function to read Odoo information from a file
def read_odoo_info(file_path, verbose):
    odoo_info = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if verbose:
                    print("Processing line:", line)
                pairs = re.findall(r"([^=]+)\s*=\s*(.*)", line)
                for key, value in pairs:
                    odoo_info[key.strip()] = value.strip().strip(
                        "'"
                    )  # Remove leading/trailing single quotes
                    if verbose:
                        print(
                            "Matched key-value pair:",
                            key.strip(),
                            ":",
                            value.strip().strip("'"),
                        )
        if verbose:
            print("Key-value pairs read from file:")
            for key, value in odoo_info.items():
                print(key + ":", value)
    except FileNotFoundError:
        raise FileNotFoundError("The specified file was not found.")
    return (
        odoo_info.get("url"),
        odoo_info.get("db"),
        odoo_info.get("username"),
        odoo_info.get("password"),
    )


def post_attendance(file_path, action, username, verbose):
    try:
        url, db, db_username, password = read_odoo_info(file_path, verbose)
    except FileNotFoundError:
        return {"message": "Credentials file not found.", "status_code": 404}, 404
    except Exception as e:
        return {"message": str(e), "status_code": 500}, 500

    try:
        common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
        uid = common.authenticate(db, db_username, password, {})
    except Exception as e:
        return {
            "message": "Error during authentication: {}".format(e),
            "status_code": 500,
        }, 500

    if not uid:
        return {"message": "Authentication failed.", "status_code": 401}, 401

    try:
        models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))

        employee_id = models.execute_kw(
            db,
            uid,
            password,
            "hr.employee",
            "search",
            [[["name", "=", username]]],
            {"limit": 1},
        )

        if not employee_id:
            return {
                "message": "Employee ID not found for user {}.".format(username),
                "status_code": 404,
            }, 404

        if action == "check-in":
            # Check for existing active attendance record
            attendance_id = models.execute_kw(
                db,
                uid,
                password,
                "hr.attendance",
                "search",
                [[["employee_id", "=", employee_id[0]], ["check_out", "=", False]]],
                {"limit": 1},
            )
            if attendance_id:
                # Employee already has an active check-in session
                return {
                    "message": "Error: Cannot clock in. {} already has an active check-in session.".format(
                        username
                    ),
                    "status_code": 400,
                }, 400
            else:
                # No active check-in found, proceed with clock-in
                result = models.execute_kw(
                    db,
                    uid,
                    password,
                    "hr.attendance",
                    "create",
                    [
                        {
                            "employee_id": employee_id[0],
                            "check_in": datetime.now(timezone.utc).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    ],
                )
                return {"message": "Check-in successful.", "status_code": 200}, 200

        elif action == "check-out":
            # Check for existing attendance record with no check-out
            attendance_id = models.execute_kw(
                db,
                uid,
                password,
                "hr.attendance",
                "search",
                [[["employee_id", "=", employee_id[0]], ["check_out", "=", False]]],
                {"limit": 1},
            )
            if attendance_id:
                models.execute_kw(
                    db,
                    uid,
                    password,
                    "hr.attendance",
                    "write",
                    [
                        [attendance_id[0]],
                        {
                            "check_out": datetime.now(timezone.utc).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        },
                    ],
                )
                return {"message": "Check-out successful.", "status_code": 200}, 200
            else:
                # No active check-in found, cannot clock out
                return {
                    "message": "Error: Cannot clock out. No active check-in found for {}.".format(
                        username
                    ),
                    "status_code": 400,
                }, 400
        else:
            return {"message": "Invalid action specified.", "status_code": 400}, 400

    except Exception as e:
        return {
            "message": "Error during operation: {}".format(e),
            "status_code": 500,
        }, 500
