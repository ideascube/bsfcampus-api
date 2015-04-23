from flask import Blueprint

bp = Blueprint("local_server", __name__)

import documents
import views