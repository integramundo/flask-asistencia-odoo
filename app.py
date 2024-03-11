from flask import Flask
app = Flask(__name__)

@app.route('/hello/<name>', methods=['GET'])
def hello_name(name):
    return f'Hello {name}'