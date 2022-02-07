from flask import render_template
from app import app, db

# error functions work very similar to view functions, but instead of taking a
# relative url via the route decorator, they take an error number via the
# errorhandler decorator


@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    # undo database change that caused the internal error
    db.session.rollback()
    return render_template("500.html"), 500
