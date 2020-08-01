from flask import Blueprint

bp = Blueprint('errors', __name__)  # errors blueprint creation

from app.errors import handlers  # set at bottom to avoid circular dependencies
