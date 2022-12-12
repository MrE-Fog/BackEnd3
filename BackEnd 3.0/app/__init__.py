from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["20 per minute"],
    storage_uri="memory://",
)

from app.views import main_routes, admin_routes, client_routes, api_routes
