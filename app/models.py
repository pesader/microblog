from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import db, login
from hashlib import md5


# the definition below is for an auxiliary table (a self referential one, to be
# more specific) so we won't make an entire Model class for it
followers = db.Table(
    "followers",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")),
)


class User(UserMixin, db.Model):
    # the UserMixin class provided by flask_login has generic implementations
    # for the methods and fields necessary to add login functionality to the
    # User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # db.relationship is used for one-to-many relationships. In this case,
    # the "one" side is the User class and the "many" side is the Post class.
    # The backref argument creates in the Post objects named "author, that
    # points back to the User whose id is used as ForeignKey.
    posts = db.relationship("Post", backref="author", lazy="dynamic")

    # representing followers in the database is non-trivial, so we'll comment
    # line by line of its definition
    followed = db.relationship(
        "User",  # the "right side" of the relationship, the "left side" is the parent class
        secondary=followers,  # the association table to be used
        primaryjoin=(followers.c.follower_id == id),  # condition to link left side with assoc table
        secondaryjoin=(followers.c.followed_id == id),  # condition to link right side with assoc table
        backref=db.backref("followers", lazy="dynamic"),  # how this relation is accessed from the right
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(followers, followers.c.followed_id == Post.user_id).filter(
            followers.c.follower_id == self.id
        )
        own = Post.query.filter(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


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
