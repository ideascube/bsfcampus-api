from flask import Blueprint, request, jsonify
from MookAPI.services import misc_activities

from . import route

bp = Blueprint('analytics', __name__, url_prefix="/analytics")
