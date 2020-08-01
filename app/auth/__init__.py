# initiates authentification blueprint to include view functions, web forms, and support functions (like password reset by email) related to authentification functionality
from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes
