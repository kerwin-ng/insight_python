import json

from flask import Flask, request

app = Flask(__name__)


@app.route('/userlogin', methods=['GET', 'POST'])
def userPhoneLogin():
    data = json.loads(request.get_data().decode('utf-8'))  # 将前端Json数据转为字典


if __name__ == '__main__':
    app.debug = True
    app.run()