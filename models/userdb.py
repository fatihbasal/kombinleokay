from db import db
from passlib.hash import pbkdf2_sha256
from sqlalchemy.dialects.postgresql import ARRAY


saved_posts = db.Table('saved_posts',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('post_id', db.Integer, db.ForeignKey('posts.id'))
                       )

class UserModel(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(200))
    name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    email = db.Column(db.String(80))
    profile_pic = db.Column(db.String(255))
    clothes = db.relationship('ClotheModel', backref='owner', lazy='dynamic')
    posts = db.relationship('PostModel', back_populates='author', lazy='dynamic',  overlaps="user")
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
    combinations = db.relationship('CombinationModel', back_populates='user', lazy='dynamic')
    survey = db.Column(ARRAY(db.Float), default=[])
    saved_posts = db.relationship('PostModel', secondary="saved_posts", backref=db.backref('saved_by_users', lazy='dynamic'))
    outfits = db.relationship('Outfit', backref='outfit_owner', lazy='dynamic')
    
    
    def to_dict(self,depth=1):
        if depth == 0:
            return {
            'id': self.id,
            'username': self.username,
            # other simple fields
        }
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'clothes': [clothe.to_dict() for clothe in self.clothes.all()],
            'posts': [post.to_dict() for post in self.posts.all()],
            'followers': [follower.follower.to_dict(depth = depth-1) for follower in self.followers.all()],
            'following': [followed.followed.to_dict(depth = depth -1) for followed in self.following.all()],
            'combinations': [combination.to_dict() for combination in self.combinations.all()],
            'survey' : self.survey,
            "saved_posts": [post.to_dict() for post in self.saved_posts],
            "profile_pic": self.profile_pic,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outfits = db.relationship('Outfit', backref='outfit_owner', lazy='dynamic')

    
