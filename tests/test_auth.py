import pytest
from flask import g, session
from flaskr.db import get_db

#登録テスト
def test_register(client,app):
    #registerページが表示できるか 200が成功500が失敗
    assert client.get('/auth/register').status_code == 200
    #ポストを発生させて登録
    response = client.post(
        '/auth/register', data={'username': 'a' , 'password' : 'a'}
    )
    #登録後、loginビューにリダイレクトするかどうかのテスト 
    assert 'http://localhost/auth/login' == response.headers['Location']

    #aというユーザーが登録されているかのテスト
    with app.app_context():
        assert get_db().execute(
                                "select * from user where username ='a' ",
                                ).fetchone() is not None

#三種類のテストデータを準備する
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_Register_vaidate_input(client,username,password,message):
    #準備したデータを実行する
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
        )

    #表示されるべきメッセージが表示されているか
    assert message in response.data

#ログインページのテスト
def test_login(client,auth):
    #表示されるか
    assert client.get('/auth/login').status_code==200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    with client:
        client.get('/')
        assert session['user_id']==1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    print(response.data)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session