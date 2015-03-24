from flask import Blueprint

bp = Blueprint("config", __name__)

import documents
import views