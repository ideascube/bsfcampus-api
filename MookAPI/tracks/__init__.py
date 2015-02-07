from flask import Blueprint

bp = Blueprint("tracks", __name__)

import documents
import views