from flask import Blueprint

bp = Blueprint("local_servers", __name__)

import documents
import views