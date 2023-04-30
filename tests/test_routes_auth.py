from unittest.mock import MagicMock

from src.database.model import User
from src.services.auth import create_access_token, create_refresh_token, create_email_token


def test_signup(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    response = client.post('/api/auth/signup', json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload['email'] == user.get('email')


def test_repeat_signup(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    response = client.post('/api/auth/signup', json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload['detail'] == 'Account already exists'


def test_login_not_confirmed(client, user):
    response = client.post('/api/auth/login', data={'username': user.get('email'), 'password': user.get('password')})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload['detail'] == 'Email not confirmed'


def test_login(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post('/api/auth/login', data={'username': user.get('email'), 'password': user.get('password')})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['token_type'] == 'bearer'


def test_login_invalid_password(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post('/api/auth/login', data={'username': user.get('email'), 'password': 'password'})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload['detail'] == 'Invalid password'


def test_login_invalid_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post('/api/auth/login', data={'username': 'email', 'password': 'password'})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload['detail'] == 'Invalid email'


def test_refresh_token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    login_response = client.post('/api/auth/login', data={'username': user.get('email'), 'password': user.get('password')})
    payload = login_response.json()
    response = client.get('/api/auth/refresh_token')
    payload = response.json()
    assert payload['detail'] == 'Not authenticated'


def test_confirmed_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    email_token = create_email_token({'sub': user.get('email')})
    response = client.get(f'/api/auth/confirmed_email/{email_token}')
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['message'] == 'Email confirmed'


def test_already_confirmed_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    email_token = create_email_token({'sub': user.get('email')})
    response = client.get(f'/api/auth/confirmed_email/{email_token}')
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['message'] == 'Your email is already confirmed'


def test_no_user_confirmed_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    email_token = create_email_token({'sub': 'email'})
    response = client.get(f'/api/auth/confirmed_email/{email_token}')
    assert response.status_code == 400, response.text
    payload = response.json()
    assert payload['detail'] == 'Verification error'


def test_request_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    request_email = {'email': user.get('email')}
    response = client.post('/api/auth/request_email', json=user)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['message'] == 'Check your email for confirmation.'


def test_confirmed_request_email(client, user, session):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    request_email = {'email': user.get('email')}
    response = client.post('/api/auth/request_email', json=user)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload['message'] == 'Your email is already confirmed'




