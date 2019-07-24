import sqlite3

import pytest
from flaskr.db import get_db

#よくわかっていない
#アプリケーションコンテキスト内では、get_db呼び出されるたびに同じ接続を返す必要があります。コンテキストの後で、接続は閉じられるべきです
def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)

#init-dbコマンドが呼び出す必要がありますinit_db機能と出力メッセージを。
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False
    def fake_init_db():
        Recorder.called = True

    #monkeypatchを使ってinit_dbが呼び出されたかどうかを返す
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called