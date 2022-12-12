import time

from flask import request, make_response

from app import app, utils
from app.config import db_player_data, player_cache


@app.route("/auth", methods=["POST"])
def auth():
    key, iv, body = utils.parse_body(request.json)
    if not body:
        return make_response(utils.create_return(key, iv, {"success": False, "message": "Couldn't parse request"}), 403)

    print("Received auth request with body", body, "from ip",
          request.headers.get("X-Forwarded-For") or request.remote_addr)

    if "api_key" not in body or "hwid" not in body or not utils.is_user_auth(body["api_key"], body["hwid"]):
        return make_response(utils.create_return(key, iv, {"success": False, "message": "Unauthorized"}), 403)
    else:
        return make_response(utils.create_return(key, iv, {"success": True}), 200)


# Manages keepalive + does stuff in the backend
@app.route("/keepalive", methods=["POST"])
def keepalive():
    key, iv, body = utils.parse_body(request.json)
    if not body:  # Sent correctly
        return make_response(utils.create_return(key, iv, {"success": False, "message": "Couldn't parse request"}), 403)

    # User auth is authd
    if "api_key" not in body or "hwid" not in body or not utils.is_user_auth(body["api_key"], body["hwid"]):
        return make_response(utils.create_return(key, iv, {"success": False, "message": "Unauthorized"}), 403)

    # Player data exists
    if "player_data" not in body or "ign" not in body or "uuid" not in body:
        return make_response(utils.create_return(key, iv, {"success": False, "message": "Formatted Wrong"}), 403)

    player_data = body["player_data"]

    # All required fields exist in player_data
    if "prestige" not in player_data or "level" not in player_data or "lobby" not in player_data or "gold" not in player_data:
        return make_response(utils.create_return(key, iv, {"success": False, "message": "Formatted Wrong"}), 403)

    entry = {"api_key": body["api_key"], "hwid": body["hwid"], "current_time": time.time_ns() // 1000000,
             "ip": request.headers.get("X-Forwarded-For") or request.remote_addr,
             "player_data": {
                 "prestige": player_data["prestige"],
                 "level": player_data["level"],
                 "lobby": player_data["lobby"],
                 "gold": player_data["gold"]
             }}

    if player_data["prestige"] != -1 and player_data["level"] != -1 and player_data["lobby"] and \
            player_data["gold"] != -1:
        db_player_data[body["uuid"]].insert_one(entry)

    to_return = []
    player_entry = player_cache.get(body["ign"])
    if player_entry:
        to_return = player_entry["commands"]

    player_cache.set(body["ign"], {"player_data": entry, "commands": []})

    return make_response(utils.create_return(key, iv, {"success": True, "commands": to_return}), 200)
