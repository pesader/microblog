from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db, login


class User(UserMixin, db.Model):
    # the UserMixin class provided by flask_login has generic implementations
    # for the methods and fields necessary to add login functionality to the
    # User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # db.relationship is used for one-to-many relationships. In this case,
    # the "one" side is the User class and the "many" side is the Post class.
    # The backref argument creates in the Post objects named "author, that
    # points back to the User whose id is used as ForeignKey.
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"<Post {self.body}>"


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
