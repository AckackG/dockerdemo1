import os
from datetime import datetime
from atexit import register
from flask import Flask, request

VERSION = 'V1.2 in github codespace'
FILESAVE_INTERVAL = 10
TRAFFIC_FILEPATH = os.path.join(os.path.dirname(__file__), 'data', 'traffic.txt')

# Globals
counter_start = datetime.utcnow().timestamp()
visits_list = []

app = Flask(__name__)

# Set host and port
HOST = '0.0.0.0'
PORT = 5000


def init():
    # Create data folder if it doesn't exist
    _dir = os.path.dirname(TRAFFIC_FILEPATH)
    if not os.path.exists(_dir):
        os.makedirs(_dir)

    global visits_list
    if os.path.exists(TRAFFIC_FILEPATH):
        with open(TRAFFIC_FILEPATH, 'r') as f:
            visits_list = f.readlines()

    register(write_traffics)


def write_traffics():
    with open(TRAFFIC_FILEPATH, 'w') as file:
        file.writelines(visits_list)

def list2html(lst):
    return ''.join(['<p>'+ x + '</p>'for x in lst[::-1]])


@app.route('/')
def index():
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    browser = user_agent.split('/')[0]
    request_method = request.method
    headers = dict(request.headers)
    query_params = dict(request.args)

    visits_list.append(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} : {ip_address} | {user_agent}\n")

    # 定时和文件交换列表
    global counter_start
    now = datetime.utcnow().timestamp()
    time_passed = now - counter_start

    if time_passed > FILESAVE_INTERVAL:
        counter_start = now
        write_traffics()

    return f'''
    <h1>Viewer Information {VERSION}</h1>
    <p><strong>IP Address:</strong> {ip_address}</p>
    <p><strong>User Agent:</strong> {user_agent}</p>
    <p><strong>Browser:</strong> {browser}</p>
    <p><strong>Request Method:</strong> {request_method}</p>
    <p><strong>Headers:</strong> {headers}</p>
    <p><strong>Query Parameters:</strong> {query_params}</p>
    <p><strong>Total Visits:</strong></p>
    <div>{list2html(visits_list)}</div>
    '''


if __name__ == '__main__':
    init()
    app.run(host=HOST, port=PORT,debug=True)
