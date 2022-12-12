import time

from flask import request, make_response

from app import app
from app.config import db_player_data, player_cache, api_cache


@app.route("/api/v1/public/command", methods=["POST"])
def command():
    if not request.headers.get("api_key"):
        return make_response({"success": False, "message": "Not Authorized"}, 403)

    if not request.json.get("bots") or not request.json.get("commmnd"):
        return make_response({"success": False, "message": "Missing fields \"bots\" or \"commmnd\""}, 400)

    for bot in request.json.get("bots"):
        if bot in player_cache and \
                player_cache.get(bot)["player_data"]["api_key"] == request.headers.get("api_key"):
            player_cache.get(bot)["commands"].append(command)

    return make_response({"success": True}, 200)


@app.route("/api/v1/public/list_bots")
def list_bots():
    if not request.headers.get("api_key"):
        return make_response({"success": False, "message": "Not Authorized"}, 403)

    if request.headers.get("api_key") in api_cache:
        return make_response(api_cache.get(request.headers.get("api_key")), 200)

    temp = {i: j["player_data"] for i, j in list_bots if j["player_data"]["api_key"] == request.headers.get("api_key")}
    api_cache.set(request.headers.get("api_key"), temp)

    return temp


@app.route("/api/v1/public/bot_info/", methods=["POST"])
def bot_info():
    if not request.headers.get("api_key"):
        return make_response({"success": False, "message": "Not Authorized"}, 403)

    if not request.json.get("bot"):
        return make_response({"success": False, "message": "Missing field \"bot\""}, 400)

    before = time.time_ns() // 1_000_000
    if request.json.get("before"):
        before = int(request.json.get("before"))

    collection = db_player_data[request.json.get("bot")]

    if collection.find_one()["api_key"] != request.headers.get("api_key"):
        return make_response({"success": False, "message": "Not Authorized"}, 403)

    responses = [i for i in
                 collection.find({"current_time": {"$lt": before}}).sort("current_time", -1).limit(100)]

    return make_response({"success": True, "data": responses}, 200)
