from flask import Flask
from urllib.parse import quote

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'SF Bots'


if __name__ == "__main__":
    app.run()
