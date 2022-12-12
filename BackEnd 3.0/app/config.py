import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import pymongo

from app.cache import Cache

client = pymongo.MongoClient(
    "mongodb+srv://autogrinder:asdifjaqoIJcdiosmciaom@cluster0.gjvvp56.mongodb.net/?retryWrites=true&w=majority")

db_player_data = client["player_data"]
db_keys = client["keys"]

admin_key = "KWluEiYyuE_blMsQWikGo_oCDtrfeDCZ"

api_cache = Cache()
player_cache = Cache(default_timeout=15)  # Also double as a keepalive

with open(os.path.join(__file__, "..", "key.pem"), "rb") as f:
    private_key = load_pem_private_key(f.read(), None, default_backend())
