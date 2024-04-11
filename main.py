import logging
import os
import threading
import time
from datetime import datetime
from atexit import register
from flask import Flask, request

# 配置Flask应用
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# 定义常量
VERSION = 'V1.3'
FILESAVE_INTERVAL = 60  # in seconds
TRAFFIC_FILEPATH = os.path.join(os.path.dirname(__file__), 'data', 'traffic.txt')
TRAFFIC_FILEPATH2 = os.path.join(os.path.dirname(__file__), 'data', 'traffic2.txt')

visits_list = []
secret_list = []

# 创建数据存储目录
DIR_PATH = os.path.dirname(TRAFFIC_FILEPATH)
if not os.path.exists(DIR_PATH):
    os.makedirs(DIR_PATH)


def list2html(lst):
    return ''.join(['<p>' + x + '</p>' for x in lst[::-1]])


def save_data():
    global visits_list, secret_list
    app.logger.info("File saved", exc_info=True)
    with open(TRAFFIC_FILEPATH, 'w') as file:
        file.writelines(visits_list)
    with open(TRAFFIC_FILEPATH2, 'w') as file:
        file.writelines(secret_list)


def savedata_routine():
    while True:
        save_data()
        time.sleep(FILESAVE_INTERVAL)


def init():
    global visits_list, secret_list
    register(save_data)

    try:
        if os.path.exists(TRAFFIC_FILEPATH):
            with open(TRAFFIC_FILEPATH, 'r') as f:
                visits_list = f.readlines()
    except Exception as e:
        print(f"Error initializing visits list: {e}")

    try:
        if os.path.exists(TRAFFIC_FILEPATH2):
            with open(TRAFFIC_FILEPATH2, 'r') as f:
                secret_list = f.readlines()
    except Exception as e:
        print(f"Error initializing visits list: {e}")


@app.route('/')
def index():
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent')
        browser = user_agent.split('/')[0] if '/' in user_agent else user_agent
        request_method = request.method
        headers = dict(request.headers)
        query_params = dict(request.args)

        visits_list.append(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} : {ip_address} | {user_agent}\n")

        return f'''
        <style>
        body {{
            font-family: sans-serif;  /* Use a modern font */
            margin: 2rem;  /* Add some margin for spacing */
        }}

        h1 {{
            text-align: center;  /* Center align the title */
        }}

        p {{
            margin-bottom: 0.5rem;  /* Add some space between paragraphs */
        }}

        .info-container {{  /* Create a container for info sections */
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;  /* Distribute evenly */
        }}

        .info-section {{   /* Style each info section */
            width: 45%;
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 5px;  /* Add rounded corners */
            margin-bottom: 1rem;
        }}

        </style>
        <h1>Viewer Information {VERSION}</h1>
        <div class="info-container">
            <div class="info-section">
                <strong>IP Address:</strong> {ip_address}
            </div>
            <div class="info-section">
                <strong>User Agent:</strong> {user_agent}
            </div>
            <div class="info-section">
                <strong>Browser:</strong> {browser}
            </div>
            <div class="info-section">
                <strong>Request Method:</strong> {request_method}
            </div>
            <div class="info-section">
                <strong>Headers:</strong> <br>
                {', '.join([f'{key}: {value}' for key, value in headers.items()])}
            </div>
            <div class="info-section">
                <strong>Query Parameters:</strong> <br>
                {', '.join([f'{key}: {value}' for key, value in query_params.items()])}
            </div>
        </div>
        <p><strong>Total Visits:</strong></p>
        <div>{list2html(visits_list)}</div>
        '''

    except Exception as e:
        return str(e), 500


@app.route('/secret_path')
def secret():
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent')
        browser = user_agent.split('/')[0] if '/' in user_agent else user_agent
        request_method = request.method
        headers = dict(request.headers)
        query_params = dict(request.args)

        secret_list.append(f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} : {ip_address} | {user_agent}\n")

        return f'''
            <html>
            <head>
                <title>Viewer Information</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }}
                    h1 {{
                        color: #333;
                        text-align: center;
                    }}
                    p {{
                        margin-bottom: 10px;
                    }}
                    strong {{
                        color: #555;
                    }}
                    div {{
                        border: 1px solid #ccc;
                        padding: 10px;
                        margin-top: 20px;
                        max-height: 200px;
                        overflow-y: auto;
                    }}
                </style>
            </head>
            <body>
                <h1>Viewer Information {VERSION}</h1>
                <p><strong>IP Address:</strong> {ip_address}</p>
                <p><strong>User Agent:</strong> {user_agent}</p>
                <p><strong>Browser:</strong> {browser}</p>
                <p><strong>Request Method:</strong> {request_method}</p>
                <p><strong>you should not see this page!</strong></p>
                <p><strong>Query Parameters:</strong> {query_params}</p>
                <p><strong>Total Visits:</strong></p>
                <div>{list2html(secret_list)}</div>
            </body>
            </html>
            '''
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    init()
    threading.Thread(target=savedata_routine, daemon=True).start()  # 启动定时保存任务
    app.run(host='0.0.0.0', port=5000, debug=False)
