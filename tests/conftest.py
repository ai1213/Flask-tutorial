import os
import tempfile
import pytest
from flaskr import create_app
from flaskr.db import get_db,init_db

#data.sqlを取得
with open(os.path.join(os.path.dirname(__file__),'data.sql'),'rb') as f:
    _data_sql = f.read().decode('utf8')

#fixture テストを実行するために必要な状態、条件
@pytest.fixture
def app():
    #一時的なdbを作成
    db_fd,db_path = tempfile.mkstemp()
    
    #テストモードであることを明記しつつappを作成
    app = create_app({
        'TESTING':True,
        'DATABASE': db_path,
        })

    #db初期化してテストデータをインサート
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    
    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    #サーバーを実行せずにアプリケーションを動かす
    return app.test_client()

@pytest.fixture
def runner(app):
    #クリックコマンドを呼び出す
    return app.test_cli_runner()

#ユーザーがログインするという動作をコードで書く
class AuthActions(object):
    def __init__(self,client):
        self._client=client
    def login(self,username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username,'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)