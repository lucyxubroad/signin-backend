import json
from db import db, Post, Comment
from flask import Flask, request

db_filename = "confessions.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

with app.app_context():
    db.create_all()
    
@app.route('/')
def hello():
  return 'Hello World!'

@app.route('/api/posts/')
def get_posts():
  """Retrieves list of all posts."""
  posts = Post.query.all()
  res = {'success': True, 'data': [post.serialize() for post in posts]}
  return json.dumps(res), 200

@app.route('/api/posts/long=<float:long>&lat=<float:lat>/')
def get_post_by_location(long, lat):
  """Retrieves list of posts made in location vicinity."""
  posts = Post.query.all()
  response_body = []
  for post in posts:
    longitude_diff = abs(post.longitude - long)
    latitude_diff = abs(post.latitude - lat)
    if (latitude_diff < 1000) and (longitude_diff < 1000):
      response_body.append(post.serialize())
  res = res = {'success': True, 'data': response_body}
  return json.dumps(res), 200

@app.route('/api/posts/', methods=['POST'])
def create_post():
  """Append new post to list."""
  post_body = json.loads(request.data)
  if 'username' in post_body and 'text' in post_body:
    post = Post (
      text = post_body.get('text'),
      username = post_body.get('username'),
      longitude = post_body.get('longitude'),
      latitude = post_body.get('latitude')
    )
    db.session.add(post)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Invalid POST body!'}), 404

@app.route('/api/post/<int:post_id>/')
def get_post(post_id):
  """Retrieve specific post in post list."""
  post = Post.query.filter_by(id=post_id).first() 
  if post is not None:
    return json.dumps({'success': True, 'data': post.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404


@app.route('/api/post/<int:post_id>/', methods=['POST'])
def edit_post(post_id):
  """Update specific post with new post"""
  post_body = json.loads(request.data)
  if 'text' not in post_body:
    return json.dumps({'success': False, 'error': 'Invalid POST body!'}), 404
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    post.text = post_body.get('text', post.text)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/', methods=['DELETE'])
def delete_post(post_id):
  """Remove specific post in post list."""
  post = Post.query.filter_by(id=post_id).first() 
  if post is not None:
    db.session.delete(post)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404 

@app.route('/api/post/<int:post_id>/comments/')
def get_comments(post_id):
  """Retrieve all comments for specific post."""
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    comments = [comment.serialize() for comment in post.comments]
    return json.dumps({'success': True, 'data': comments}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/comment/', methods=['POST'])
def post_comment(post_id):
  """Append new comment to a post."""
  post_body = json.loads(request.data)
  post = Post.query.filter_by(id=post_id).first()
  if post is not None and 'username' in post_body and 'text' in post_body:
    comment = Comment(
      text = post_body.get('text'),
      username = post_body.get('username'),
      post_id=post.id
    )
    post.comments.append(comment)
    db.session.add(comment)
    db.session.commit()
    return json.dumps({'success': True, 'data': comment.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

@app.route('/api/post/<int:post_id>/vote/', methods=['POST'])
def vote_post(post_id):
  """Vote on a post."""
  post_body = json.loads(request.data)
  post = Post.query.filter_by(id=post_id).first()
  if post is not None:
    if post_body['vote'] or 'vote' not in post_body:
      post.score = post.score + 1
    else:
      post.score = post.score - 1
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Invalid post!'}), 404

@app.route('/api/comment/<int:comment_id>/vote/', methods=['POST'])
def vote_comment(comment_id):
  post_body = json.loads(request.data)
  comment = Comment.query.filter_by(id=comment_id).first()
  if comment is not None:
    if post_body['vote'] or 'vote' not in post_body:
      comment.score = comment.score + 1
    else:
      comment.score = comment.score - 1
    db.session.commit()
    return json.dumps({'success': True, 'data': comment.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Invalid comment!'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
