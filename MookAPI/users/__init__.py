from flask import Blueprint

bp = Blueprint("users", __name__)

import documents
import views
from flask.ext.security.forms import RegisterForm, TextField, BooleanField, Required


class ExtendedRegisterForm(RegisterForm):
    full_name = TextField('Full Name', [])
    accept_cgu = BooleanField('Accept CGU', [Required()])

