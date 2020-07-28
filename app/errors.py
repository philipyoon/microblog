from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):  # error function for 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):  # error function for 500 database error
    db.session.rollback()  # rollback any errors so database doesn't break
    return render_template('500.html'), 500
