# This webpage serves the routes for browser stuff

from app import app
from flask import request


@app.route("/")
def main():
    print("Request Ip: ", request.headers.get("X-Forwarded-For"))
    print("Request Ip: ", request.remote_addr)

    print(request.headers)
    return "Hi"

# Request Ip:  None
# Request Ip:  127.0.0.1
# Host: 127.0.0.1:5000
# User-Agent: python-requests/2.26.0
# Accept-Encoding: gzip, deflate
# Accept: */*
# Connection: keep-alive