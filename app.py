import json
import os
import datetime

from flask import Flask, render_template, request, redirect, session, make_response
import pymysql
from flask_sqlalchemy import SQLAlchemy

pymysql.install_as_MySQLdb()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost:3306/pro?charset=utf8mb4"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = 'THIS IS A DOG'
app.debug = True
db = SQLAlchemy(app)


class Category(db.Model):

    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    cate_name = db.Column(db.String(128))
    # 增加与Topic之间的关联关系和反向引用
    topics = db.relationship('Topic', backref='category', lazy='dynamic')

    def __init__(self, cate_name):
        self.cate_name = cate_name

    def __repr__(self):
        return "<Category: %r>" % self.cate_name


class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String(128))
    # 增加与Topic之间的关联关系和反向引用
    topics = db.relationship('Topic', backref='tag', lazy='dynamic')

    def __init__(self, type_name):
        self.type_name = type_name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    loginname = db.Column(db.String(128), nullable=False)
    loginpwd = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    signature = db.Column(db.String(1024), default='个性签名... ...')
    phone = db.Column(db.String(32), nullable=True)
    userhead = db.Column(db.String(128), default='default.png')
    career = db.Column(db.String(128), nullable=True, default='无')
    music_id = db.Column(db.Integer, db.ForeignKey('music.id'), default=1)
    # 增加与Topic之间的关联关系和反向引用
    topics = db.relationship('Topic', backref='user', lazy='dynamic')
    # 增加与Reply之间的关联关系和反向引用
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    # 增加与Topic之间的关联关系和反向引用(多对多)
    view_topics = db.relationship(
        'Topic',
        secondary='voke',
        lazy='dynamic',
        backref=db.backref('viewers', lazy='dynamic')
    )

    def __repr__(self):
        return '<User: %r>' % self.loginname


class Topic(db.Model):
    __tablename__ = 'topic'
    id = db.Column(db.Integer, primary_key=True)
    # 标题
    title = db.Column(db.String(256), nullable=False, default='无')
    # 内容
    content = db.Column(db.Text, nullable=True)
    # 存帖子图片名
    image = db.Column(db.String(128), nullable=True)
    # 帖子中视频名
    video = db.Column(db.String(128), nullable=True)
    # 发帖时间,数据库中设置了自动添加
    time = db.Column(db.TIMESTAMP, default=datetime.datetime.now())
    # 浏览数
    readcount = db.Column(db.Integer, default=0)
    # 该帖子赞的数量
    thumb = db.Column(db.Integer, default=0)
    # 关系:一(tag)对多(topic)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), default=1)
    # 关系:一(Category)对多(Topic)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), default=1)
    # 关系:一(User)对多(Topic)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 增加对Comment的关联关系和反向引用
    comments = db.relationship('Comment', backref='topic', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(2048), nullable=True)
    time = db.Column(db.TIMESTAMP, default=datetime.datetime.now())
    thumb = db.Column(db.Integer, default=0)
    # 关系:一(Topic)对多(Reply)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    # 关系:一(User)对多(Reply)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Music(db.Model):
    __tablename__ = 'music'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128))
    musicname = db.Column(db.String(128))
    singer = db.Column(db.String(128))
    album = db.Column(db.String(128))
    users = db.relationship('User', backref='music', lazy='dynamic')

    def __repr__(self):
        return "<Music: %r>" % self.musicname


Voke = db.Table(
    'voke',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('viewer_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'))
)


# 提交创建所有表格
db.create_all()


@app.route('/index')
@app.route('/')
def index():
    if 'loginname' in session:
        loginname = session['loginname']
        user = User.query.filter_by(loginname=loginname).first()
        return render_template('index.html', params=locals())
    else:
        if 'loginname' in request.cookies:
            loginname = request.cookies['loginname']
            session['loginname'] = loginname
            user = User.query.filter_by(loginname=loginname).first()
            return render_template('index.html', params=locals())
        else:
            return render_template('index.html', params=locals())


@app.route('/my',methods=['GET', 'POST'])
def my_views():
    if request.method=="GET":
        # method为GET
        if 'loginname' in session:
            # 如果session中有登陆信息,直接登陆
            topics=Topic.query.order_by("id desc").all()
            loginname = session['loginname']
            user = User.query.filter_by(loginname=loginname).first()
            return render_template("my.html", params=locals())
        else:
            # session中没有登陆信息
            if 'loginname' in request.cookies:
                # cookies中有登陆信息(登录时记住了密码),将登陆信息拿出来存session,然后直接登陆
                loginname = request.cookies['loginname']
                session['loginname'] = loginname
                user = User.query.filter_by(loginname=loginname).first()
                return render_template('my.html', params=locals())
            else:
                # session和cookies中都没有登陆信息,转去登陆页面
                return redirect('/login')
    else:
        topics = Topic.query.order_by("id desc").all()
        topic=Topic()
        loginname = session['loginname']
        user = User.query.filter_by(loginname=loginname).first()
        print(loginname, user)
        print(user.id)
        # 创建一个图片对象
        topic.user_id = user.id
        if request.form.get("div"):
            topic.content = request.form.get("div")
        if request.files.get('picture', ''):
            f = request.files['picture']
            # 处理文件名称，并赋值给topic.image
            ftime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            ext = f.filename.split('.')[1]
            filename = ftime + '.' + ext
            # 将文件保存至服务器
            basedir = os.path.dirname(__file__)
            print(basedir)
            upload_path = os.path.join(basedir, 'static/upload', filename)
            f.save(upload_path)
            topic.image = filename
        if request.files.get('video', ''):
            v = request.files['video']
            # 处理视频文件名称，并赋值给topic.video
            vtime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            vext = v.filename.split('.')[-1]
            vfilename = vtime + '.' + vext
            topic.video = vfilename
            # 将文件保存至服务器
            basedir = os.path.dirname(__file__)
            upload_path = os.path.join(basedir, 'static/upload', vfilename)
            v.save(upload_path)

        db.session.add(topic)
    # return render_template('my.html', params=locals())
    return redirect('/my')


@app.route('/login', methods=['GET', 'POST'])
def login_views():
    if request.method == 'GET':
        if request.referrer:
            origin_url = request.referrer
            # if origin_url == 'http://127.0.0.1:5000/login':
            origin_url = '/'
        else:
            origin_url = '/'
        print('origin_url:', origin_url)
        # method为GET
        if 'loginname' in session:
            # 如果session中有loginname,直接跳转到来源页面
            return redirect(origin_url)
        else:
            # 如果session中没有loginname
            if 'loginname' in request.cookies:
                # 如果cookie中有loginname,将loginname保存进session,跳转到来源页面
                loginname = request.cookies['loginname']
                session['loginname'] = loginname
                return redirect(origin_url)
            else:
                # session和cookie中都没有loginname,进入登录页面
                resp = make_response(render_template('login.html'))
                resp.set_cookie('origin_url', origin_url, 60 * 60)
                return resp
    else:
        # method为POST
        # 判断用户名密码是否正确
        loginname = request.form.get('loginname')
        loginpwd = request.form.get('loginpwd')
        origin_url = request.cookies.get('origin_url', '/')
        user = User.query.filter(User.loginname == loginname, User.loginpwd == loginpwd).first()
        if user:
            # 用户名密码正确
            resp = redirect(origin_url)
            # 判断是否勾选记住密码
            print('loginname:', loginname)
            print('user:', user)
            session['loginname'] = loginname
            if 'isSave' in request.form:
                # 记住密码,将loginname存进cookie
                resp.set_cookie('loginname', loginname, 60 * 60)
                return resp
            else:
                # 不记住密码
                return resp
# 用户名密码不正确,重新到登录页面
        else:
            return redirect('/login')


@app.route('/upload-music', methods=['GET', 'POST'])
def upload_music_views():
    if request.method=="GET":
        # method为GET
        if 'loginname' in session:
            # 如果session中有登陆信息,直接登陆
            topics = Topic.query.order_by("id desc").all()
            loginname = session['loginname']
            user = User.query.filter_by(loginname=loginname).first()
            musics = Music.query.all()
            return render_template("upload_music.html", params=locals())
        else:
            # session中没有登陆信息
            if 'loginname' in request.cookies:
                # cookies中有登陆信息(登录时记住了密码),将登陆信息拿出来存session,然后直接登陆
                loginname = request.cookies['loginname']
                session['loginname'] = loginname
                user = User.query.filter_by(loginname=loginname).first()
                musics = Music.query.all()
                return render_template('upload_music.html', params=locals())
            else:
                # session和cookies中都没有登陆信息,转去登陆页面
                return redirect('/login')
    else:
        f = request.files['music']
        musicname = request.form.get('musicname', '无')
        singer = request.form.get('singer', '无')
        album = request.form.get('album', '无')
        ftime = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        filename = ftime + '.' + f.filename.split('.')[-1]
        basedir = os.path.dirname(__file__)
        path = os.path.join(basedir, 'static/upload/', filename)
        f.save(path)
        music = Music()
        music.filename = filename
        music.musicname = musicname
        music.singer = singer
        music.album = album
        loginname = session['loginname']
        user = User.query.filter_by(loginname=loginname).first()
        db.session.add(music)
        music = Music.query.filter_by(filename=filename).first()
        user.music_id = music.id

        return redirect('/upload-music')


@app.route('/liuyan', methods=['GET', 'POST'])
def liuyan_views():
    if request.method == "GET":
        # mag = Topic.query.order_by("id desc").all()
        # return render_template("my.html", params=locals())
        pass
    else:
        msg=request.form.get("liuyan")
        topicid=request.form.get("topicid")
        loginname = session['loginname']
        user = User.query.filter_by(loginname=loginname).first()
        comment = Comment()
        comment.user_id = user.id
        comment.content = msg
        comment.topic_id = topicid
        db.session.add(comment)
        print('评论存入数据库...')
    return redirect('/my')


@app.route('/delete/<tid>', methods=['GET', 'POST'])
def delete_views(tid):
    if request.method == "GET":
        pass
        # mag = Topic.query.order_by("id desc").all()
        # return render_template("my.html", params=locals())
    else:
        tid = tid
        topic = Topic.query.filter_by(id=tid).first()
        db.session.delete(topic)
    return redirect('/my')


@app.route('/test')
def test_views():
    return render_template('test.html')


@app.route('/register', methods=['GET', 'POST'])
def register_views():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        loginname = request.form.get('loginname')
        loginpwd = request.form. get('loginpwd')
        email = request.form.get('email')
        user = User()
        user.loginname = loginname
        user.loginpwd = loginpwd
        user.email = email
        db.session.add(user)
        session['loginname'] = loginname
        return redirect('/')


@app.route('/check_loginname')
def check_loginname():
    loginname = request.form.get('loginname')
    users=db.session.query(User).filter_by(loginname=loginname).first()
    if users:
        dic={
            'status':1,
            'msg':'用户名已存在,请重新输入'
        }
    else:
        dic={
            'status':0,
            'msg':'通过'
        }
    return json.dumps(dic)


@app.route('/logout')
def logout_views():
    response = redirect('/')
    if 'loginname' in session:
        del session['loginname']
    if 'loginname' in request.cookies:
        response.delete_cookie('loginname')
    return response


@app.route('/info', methods=['GET', 'POST'])
def modify_info_views():
    if request.method == 'GET':
        loginname = session['loginname']
        user = User.query.filter_by(loginname=loginname).first()
        return render_template('modify_info.html', params=locals())
    else:
        loginname = session['loginname']
        user = User.query.filter_by(loginname=loginname).first()
        username = request.form.get('username', '无')
        signature = request.form.get('signature', '无')
        phone = request.form.get('phone', '无')
        career = request.form.get('career', '无')
        user.username = username
        user.signature = signature
        user.phone = phone
        user.career = career
        if 'userhead' in request.files:
            print('有头像...')
            f = request.files['userhead']
            ftime = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            filename = ftime + '.' + f.filename.split('.')[-1]
            basedir = os.path.dirname(__file__)
            path = os.path.join(basedir, 'static/images/', filename)
            f.save(path)
            print('保存成功...')
            user.userhead = filename
        db.session.add(user)
        return redirect('/')


















if __name__ == '__main__':
    app.run(host='0.0.0.0')





















