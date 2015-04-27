from flask import Blueprint

bp = Blueprint("synchronizer", __name__)

import documents
import views