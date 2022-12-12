from base64 import b64decode, b64encode
import json
import random
import time

from Cryptodome.Cipher import AES
from cryptography.hazmat.primitives.asymmetric import padding

from app.config import private_key, db_keys


def parse_body(body):
    if "data" not in body or "encryptedKey" not in body or "encryptedIv" not in body:
        return b"", b"", {}

    aes_key = private_key.decrypt(b64decode(body["encryptedKey"]), padding.PKCS1v15())
    aes_iv = b64decode(body["encryptedIv"])
    to_decrypt = b64decode(body["data"])

    cipher = AES.new(aes_key, AES.MODE_CBC, iv=aes_iv)
    temp = cipher.decrypt(to_decrypt).decode("utf-8")

    return aes_key, aes_iv, json.loads(temp[:temp.rindex("}") + 1])


def create_return(key, iv, to_return):
    to_encrypt = json.dumps(to_return)

    cipher = AES.new(key, AES.MODE_CBC, iv=iv)

    b = to_encrypt.encode("utf-8")
    b += b"\x04" * (16 - (len(b) % 16))

    return b64encode(cipher.encrypt(b))


def is_user_auth(key, hwid):
    # Looks like {api_key: key, hwid: hwid, expire_by: expire_by, discord_id: discord_id}
    active_keys = db_keys["active"]
    entry = active_keys.find_one({"api_key": key})

    if not entry:
        return False

    # Key expired
    if time.time_ns() // 1_000_000 > entry["expire_by"]:
        active_keys.delete_many({"api_key": key})
        return False

    # HWID wrong
    if entry["hwid"] == "UNKNOWN":
        entry["hwid"] = hwid
        active_keys.update_one({"api_key": key}, {"$set": {"hwid": hwid}})
    elif entry["hwid"] != "ANY" and hwid != entry["hwid"]:
        return False
    return True


def generate_key(user):
    return "_".join(
        "".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890") for __ in range(10)) for
        _ in range(3)) + "_" + user
