from app import app, db
from app.models import User, Post

@app.shell_context_processor
def make_shell_context():
    # run "flask shell" in a terminal to get a python interpreter pre loaded
    # with definitions related to the context of your Flask project (the ones
    # defined below
    return {'db': db, 'User': User, 'Post': Post}

