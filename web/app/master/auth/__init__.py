from flask import Blueprint

auth = Blueprint("auth", __name__, template_folder = "views", static_folder = "static", static_url_path = "/auth/static")

from . import views