from flask import Blueprint, jsonify

from MookAPI.services import static_pages

from . import route

bp = Blueprint('static_pages', __name__, url_prefix="/static_pages")


@route(bp, "/<page_id>")
def get_static_page(page_id):
    return static_pages.get(page_id=page_id)

@route(bp, "/")
def all_static_pages():
    return static_pages.all()
