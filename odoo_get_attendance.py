import xmlrpc.client
import re


# Function to read Odoo information from a file
def read_odoo_info(file_path):
    odoo_info = {}
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            pairs = re.findall(r"([^=]+)\s*=\s*(.*)", line)
            for key, value in pairs:
                odoo_info[key.strip()] = value.strip().strip(
                    "'"
                )  # Remove leading/trailing single quotes
    return (
        odoo_info.get("url"),
        odoo_info.get("db"),
        odoo_info.get("username"),
        odoo_info.get("password"),
    )


def get_attendance(file_path, username, verbose):
    # Read Odoo information from the file
    try:
        url, db, db_username, password = read_odoo_info(file_path)
    except FileNotFoundError:
        return "File not found: " + file_path, 404

    # Connect to Odoo server
    try:
        common = xmlrpc.client.ServerProxy("{}/xmlrpc/2/common".format(url))
        uid = common.authenticate(db, db_username, password, {})
    except Exception as e:
        return "Error connecting to Odoo server: " + str(e), 500

    if uid:
        try:
            models = xmlrpc.client.ServerProxy("{}/xmlrpc/2/object".format(url))

            # Find the employee's ID based on the associated user's name
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
                # Retrieve attendance entries for the employee
                attendance_entries = models.execute_kw(
                    db,
                    uid,
                    password,
                    "hr.attendance",
                    "search_read",
                    [[["employee_id", "=", employee_id[0]]]],
                )

                if attendance_entries:
                    result = "Attendance Entries for {}:\n".format(username)
                    for entry in attendance_entries:
                        result += "Check-in: {}\n".format(entry["check_in"])
                        result += "Check-out: {}\n".format(entry["check_out"])
                        result += "\n"
                    return result
                else:
                    return "No attendance entries found for {}.".format(username), 404
            else:
                return "Employee ID not found for user {}.".format(username), 404
        except Exception as e:
            return "Error retrieving attendance: " + str(e), 500
    else:
        return "Authentication failed.", 401
