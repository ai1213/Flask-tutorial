import functools
from flask import (
    Blueprint,flash,g,redirect,render_template,request,session,url_for
)
from werkzeug.security import check_password_hash,generate_password_hash
from flaskr.db import get_db
import click


bp=Blueprint('auth',__name__,url_prefix='/auth'  )
#/registerのアドレスをたたくとregister()を実行する
@bp.route('/register',methods=('GET','POST'))
def register():
    #送信ボタンを押されたとき、みたいな画面側からのリクエストが発生したとき
    if request.method == 'POST':
        #入力の検証。username と passwordを受け取って
        username = request.form['username']
        password = request.form['password']

        #DB取得して
        db=get_db()

        error = None

        #未入力のチェック
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        #usernameがかぶっているかチェック
        elif db.execute("SELECT id FROM  user WHERE  username = ?",(username,)).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)
        
        #エラーがなければDBに登録
        if error is None:
            db.execute('INSERT INTO user (username,password) VALUES (? ,?)',
                        (username,generate_password_hash(password)))
            db.commit()
            #ログイン画面を表示
            return redirect(url_for('auth.login'))

        #エラーをフラッシュで表示
        flash(error)
    #登録画面に戻る
    return render_template('auth/register.html')

#/ログイン画面
@bp.route('/login',methods=('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password= request.form['password']
        db = get_db()
        error =None
        user = db.execute( "SELECT * FROM user WHERE username = ?",(username,)).fetchone()

        if user is None:
            error = "Incorrent username."
        elif not check_password_hash(user['password'],password):
            error ='Incorrect password.'

        if error is None:
            session.clear()
            session['user_id']=user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

#どんな画面でも描画前にuserを取得しなおす
@bp.before_app_request
def load_logged_in_user():
    user_id=session.get('user_id')
    click.echo('user_id' + str(user_id))
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user Where id = ?', (user_id,)).fetchone()

#logout画面
@bp.route('/logout')
def logout():
    #セッションを消してインデックスに戻る
    session.clear()


    return redirect(url_for('index'))

#ブログ投稿を作成、編集、削除するには、ログインする必要があります。デコレータを使用して、適用されているビューごとにこれを確認できます
#このデコレータは、適用された元のビューをラップする新しいビュー関数を返します。新しい関数は、ユーザーがロードされているかどうかを確認し、
# それ以外の場合はログインページにリダイレクトします。ユーザーがロードされると、元のビューが呼び出されて通常どおり続行されます。
# ブログビューを書くときにこのデコレータを使います。
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
    
        click.echo('login_required user_id' + str(g.user))
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view