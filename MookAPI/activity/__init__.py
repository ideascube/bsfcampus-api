from flask import Blueprint

bp = Blueprint("activity", __name__)

import documents
import views