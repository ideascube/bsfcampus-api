from flask import Blueprint

bp = Blueprint("resources", __name__)

import documents
import views

import hierarchy
