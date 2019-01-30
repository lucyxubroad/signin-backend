import json
from db import db, User, Event
from flask import Flask, request

import users_dao

db_filename = "signin.db"
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

# get all events - works!
@app.route('/api/events/')
def get_events():
  events = Event.query.all()
  res = {'success': True, 'data': [event.serialize() for event in events]}
  return json.dumps(res), 200

# creating a new event - works
@app.route('/api/events/', methods=['POST'])
def create_event():
  post_body = json.loads(request.data)
  event = Event (
    event = post_body.get('event'),
    club = post_body.get('club'),
    location = post_body.get('location'),
    description = post_body.get('description'),
    event_creator = post_body.get('event_creator')
  )
  creator_id = post_body.get('event_creator')
  creator = User.query.filter_by(id=creator_id).first()
  creator.created_events.append(event)
  db.session.add(event)
  db.session.commit()
  return json.dumps({'success': True, 'data': event.serialize()}), 200

# LUCY: Repurpose to support events - works!
@app.route('/api/<int:user_id>/events/')
def get_user_events(user_id):
  user = User.query.filter_by(id=user_id).first() 
  if user is not None:
    events = [event.serialize() for event in user.created_events]
    return json.dumps({'success': True, 'data': events}), 200
  return json.dumps({'success': False, 'error': 'User not found!'}), 404

# does not work! 
@app.route('/api/event/<int:event_id>/signin/', methods=['POST'])
def signin_event(event_id):
  post_body = json.loads(request.data)
  event = Event.query.filter_by(id=event_id).first()
  user_id = post_body.get('user_id')
  user = User.query.filter_by(id=user_id).first()
  if event is not None:
    event.attendees.append(user)
    db.session.commit()
    return json.dumps({'success': True, 'data': event.serialize()}), 200
  return json.dumps({'success': False, 'error': 'Post not found!'}), 404

# does not work!
@app.route('/api/event/<int:event_id>/attendees/')
def get_event_attendees(event_id):
  event = Event.query.filter_by(id=event_id).first() 
  if event is not None:
    users = [user.serialize() for user in event.attendees]
    db.session.commit()
    return json.dumps({'success': True, 'data': users}), 200
  return json.dumps({'success': False, 'error': 'Event not found!'}), 404 

# works!
@app.route('/register/', methods=['POST'])
def register_account():
    post_body = json.loads(request.data)
    email = post_body.get('email')
    password = post_body.get('password')
    first_name = post_body.get('first_name')
    last_name = post_body.get('last_name')

    if email is None or password is None or first_name is None or last_name is None:
        return json.dumps({'error': 'Invalid field'})

    created, user = users_dao.create_user(email, password, first_name, last_name)

    if not created:
        return json.dumps({'error': 'User already exists.'})

    return json.dumps({
        'session_token': user.session_token,
        'session_expiration': str(user.session_expiration),
        'update_token': user.update_token,
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'id': user.id
        }
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
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email, 
            'id': user.id
        }
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
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'id': user.id
        }
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

def extract_token(request):
  auth_header = request.headers.get('Authorization')
  if auth_header is None:
      return False, json.dumps({'error': 'Missing authorization header.'})

  bearer_token = auth_header.replace('Bearer ', '').strip()
  if bearer_token is None or not bearer_token:
      return False, json.dumps({'error': 'Invalid authorization header.'})

  return True, bearer_token