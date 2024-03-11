from flask import Flask, request
from odoo_attendance import get_attendance

app = Flask(__name__)

@app.route('/hello/<name>', methods=['GET'])
def hello_name(name):
    return f'Hello {name}'

@app.route('/get_attendance', methods=['GET'])
def get_attendance_route():
    file_path = request.args.get('file_path')
    username = request.args.get('username')
    verbose = request.args.get('verbose', False)

    result = get_attendance(file_path, username, verbose)
    return result

if __name__ == '__main__':
    app.run(debug=True)
