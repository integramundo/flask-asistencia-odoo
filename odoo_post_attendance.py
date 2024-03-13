import xmlrpc.client
import re
import sys
from datetime import datetime, timezone


def post_attendance(file_path, action, username, verbose):
    # Function to read Odoo information from a file
    def read_odoo_info(file_path):
        odoo_info = {}
        with open(file_path, "r") as file:
            for line in file:
                line = line.strip()
                if verbose == True:
                    print("Processing line:", line)
                pairs = re.findall(r"([^=]+)\s*=\s*(.*)", line)
                for key, value in pairs:
                    odoo_info[key.strip()] = value.strip().strip(
                        "'"
                    )  # Remove leading/trailing single quotes
                    if verbose == True:
                        print(
                            "Matched key-value pair:",
                            key.strip(),
                            ":",
                            value.strip().strip("'"),
                        )
        if verbose == True:
            print("Key-value pairs read from file:")
            for key, value in odoo_info.items():
                print(key + ":", value)
        return (
            odoo_info.get("url"),
            odoo_info.get("db"),
            odoo_info.get("username"),
            odoo_info.get("password"),
        )

    try:
        url, db, db_username, password = read_odoo_info(file_path)
    except FileNotFoundError:
        return "File not found:", 404

    common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
    uid = common.authenticate(db, db_username, password, {})

    if uid:
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

        if employee_id:
            if action == "check-in":
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
                return "Check-in successful."
            elif action == "check-out":
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
                    return "Check-out successful."
                else:
                    return "No active check-in found for {}.".format(username), 404
        else:
            return "Employee ID not found for user {}.".format(username), 404
    else:
        return "Authentication failed.", 401
