from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    comments = db.relationship('Comment', cascade='delete')

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', '')
        self.username = kwargs.get('username', '')
        self.score = kwargs.get('score', 0)
        self.longitude = kwargs.get('longitude', 0)
        self.latitude = kwargs.get('latitude', 0)

    def serialize(self):
        return {
            'id': self.id,
            'score': self.score,
            'text': self.text,
            'username': self.username,
            'longitude': self.longitude,
            'latitude': self.latitude
        }

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __init__(self, **kwargs):
        self.text = kwargs.get('text', '')
        self.username = kwargs.get('username', '')
        self.score = kwargs.get('score', 0)
        self.post_id = kwargs.get('post_id')

    def serialize(self):
        return {
            'id': self.id,
            'score': self.score,
            'text': self.text,
            'username': self.username,
            'post_id': self.post_id
        }
