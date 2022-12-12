import time

from flask import request, make_response

from app import app, limiter, config, utils
from app.config import db_keys, player_cache


@app.route("/api/v1/admin/list_all")
@limiter.exempt
def list_all():
    if request.headers.get("token") != config.admin_key:
        return make_response({"success": False, "message": "Not Authorized"}, 403)
    return make_response({i: j["player_data"] for i, j in player_cache}, 200)


@app.route("/api/v1/admin/hwid", methods=["POST"])
@limiter.exempt
def delete_hwid():
    if request.headers.get("token") != config.admin_key:
        return make_response({"success": False, "message": "Not Authorized"}, 403)

    if not request.json.get("api_key"):
        return make_response({"success": False, "message": "No api key specified"}, 400)

    active_keys = db_keys["active"]
    entry = active_keys.find_one({"api_key": request.json.get("api_key")})

    if not entry:
        return make_response({"success": False, "message": "Could not find api key"}, 400)
    else:
        active_keys.update_one({"api_key": request.json.get("api_key")}, {"$set": {"hwid": "UNKNOWN"}})


@app.route("/api/v1/admin/create_key", methods=["POST"])
@limiter.exempt
def create_key():
    if request.headers.get("token") != config.admin_key:
        return make_response({"success": False, "message": "Not Authorized"}, 403)

    if not request.json.get("discord_id") and not request.json.get("discord_name"):
        return make_response({"success": False, "message": "Missing \"discord_id\" or \"discord_name\" fields"}, 400)

    key = utils.generate_key(request.json.get("discord_name"))

    if request.json.get("timeout"):
        timeout = request.json.get("timeout")
    else:
        timeout = time.time_ns() // 1_000_000 + 315360000000  # 10 Years

    db_keys["active"].insert_one(
        {"api_key": key, "hwid": "UNKNOWN", "expire_by": timeout, "discord_id": request.json.get("discord_id")}
    )

    return make_response({"success": True, "key": key}, 200)


@app.route("/api/v1/admin/delete_key", methods=["POST"])
@limiter.exempt
def delete_key():
    if request.headers.get("token") != config.admin_key:
        return make_response({"success": False, "message": "Not Authorized"}, 403)

    if not request.json.get("api_key"):
        return make_response({"success": False, "message": "Missing \"api_key\" field"}, 400)

    db_keys["active"].delete_many({"api_key": request.json.get("api_key")})

    return make_response({"success": True}, 200)
