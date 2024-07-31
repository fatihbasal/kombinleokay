from db import db
from passlib.hash import pbkdf2_sha256

class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    clothes = db.relationship('ClotheModel', backref='owner', lazy='dynamic')
    posts = db.relationship('PostModel', back_populates='author', lazy='dynamic', overlaps="user")
    followers = db.relationship(
        'FollowModel',
        foreign_keys='FollowModel.followed_id',
        backref=db.backref('followed', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    following = db.relationship(
        'FollowModel',
        foreign_keys='FollowModel.follower_id',
        backref=db.backref('follower', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'clothes': [clothe.to_dict() for clothe in self.clothes.all()],
            'posts': [post.to_dict() for post in self.posts.all()],
            'followers': [follower.follower_id for follower in self.followers],
            'following': [followed.followed_id for followed in self.following]
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            id=data.get('id'),
            username=data.get('username'),
            name=data.get('name'),
            surname=data.get('surname'),
            email=data.get('email'),
            password=pbkdf2_sha256.hash(data.get('password'))
        )
        return user


def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserModel.query.filter_by(id=identity).one_or_none()
