import json
from db import db, Post, Comment, User
from flask import Flask, request

from math import sin, cos, sqrt, atan2, radians
import datetime
import users_dao

db_filename = "signin.db"
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % db_filename
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)

with app.app_context():
    db.create_all()
    
# LUCY: Need this for supporting users. Revisit details later.
def extract_token(request):
  auth_header = request.headers.get('Authorization')
  if auth_header is None:
      return False, json.dumps({'error': 'Missing authorization header.'})

  # Header looks like "Authorization: Bearer <session token>"
  bearer_token = auth_header.replace('Bearer ', '').strip()
  if bearer_token is None or not bearer_token:
      return False, json.dumps({'error': 'Invalid authorization header.'})

  return True, bearer_token

@app.route('/')
def hello():
  return 'Hello World!'

# LUCY: Repurpose to support events
@app.route('/api/posts/')
def get_posts():
  """Retrieves list of all posts."""
  posts = Post.query.all()
  res = {'success': True, 'data': [post.serialize() for post in posts]}
  return json.dumps(res), 200

# LUCY: Repurpose to support events
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

# LUCY: Repurpose to support events
@app.route('/api/post/<int:post_id>/')
def get_post(post_id):
  """Retrieve specific post in post list."""
  post = Post.query.filter_by(id=post_id).first() 
  if post is not None:
    return json.dumps({'success': True, 'data': post.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

# LUCY: Repurpose to support events
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

# LUCY: Repurpose to support events
@app.route('/api/post/<int:post_id>/', methods=['DELETE'])
def delete_post(post_id):
  """Remove specific post in post list."""
  post = Post.query.filter_by(id=post_id).first() 
  if post is not None:
    db.session.delete(post)
    db.session.commit()
    return json.dumps({'success': True, 'data': post.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404 

# LUCY: Need this for supporting users. Revisit details later.
@app.route('/register/', methods=['POST'])
def register_account():
    post_body = json.loads(request.data)
    email = post_body.get('email')
    password = post_body.get('password')

    if email is None or password is None:
        return json.dumps({'error': 'Invalid email or password'})

    created, user = users_dao.create_user(email, password)

    if not created:
        return json.dumps({'error': 'User already exists.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token,
        'user_id': user.id,
        'photo_id': user.id%5
    })

# LUCY: Need this for supporting users. Revisit details later.
@app.route('/login/', methods=['POST'])
def login():
    post_body = json.loads(request.data)
    email = post_body.get('email')
    password = post_body.get('password')

    if email is None or password is None:
        return json.dumps({'error': 'Invalid email or password'})

    success, user = users_dao.verify_credentials(email, password)

    if not success:
        return json.dumps({'error': 'Incorrect email or password.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token,
        'user_id': user.id,
        'photo_id': user.id%5
    })

# LUCY: Need this for supporting users. Revisit details later.
@app.route('/session/', methods=['POST'])
def update_session():
    success, update_token = extract_token(request)

    if not success:
        return update_token

    try:
        user = users_dao.renew_session(update_token)
    except: 
        return json.dumps({'error': 'Invalid update token.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token,
        'user_id': user.id,
        'photo_id': user.id%5
    })

# LUCY: Need this for supporting users. Revisit details later.
@app.route('/secret/', methods=['GET'])
def secret_message():
    success, session_token = extract_token(request)

    if not success:
        return session_token 

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({'error': 'Invalid session token.'})

    return json.dumps({'message': 'You have successfully implemented sessions.'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
