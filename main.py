#!/usr/bin/python3
from flask import Flask,render_template,url_for,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager,login_required,login_user,logout_user
from user import User
import forms
import database

app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bookquery',methods=['GET','POST'])
def bookquery():
    form = forms.BookQueryForm()
    result = []
    if form.validate_on_submit():
        result = database.book_search(form,all_table['book'])
    return render_template('bookquery.html',form=form,list=result)

@app.route('/login',methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        admintable = all_table['admin']
        user = db.session.query(admintable).filter_by(name=form.name.data).first()
        if user is not None:
            user = User(user._mapping)
            if user.password == form.password.data:
                login_user(user)
                return redirect(url_for('index'))
        flash('用户名或密码不正确')
    
    return render_template('login.html', form=form)

@app.route('/bookman',methods=['GET', 'POST'])
@login_required
def bookman():
    form_add = forms.BookAddForm()
    form_del = forms.BookDeleteForm()

    if form_add.validate_on_submit() and form_add.submitadd.data:
        database.book_add(form_add,all_table)
    if form_del.validate_on_submit() and form_del.submitdel.data:
        database.book_delete(form_del,all_table)
            
    return render_template('bookman.html',form_add=form_add,form_del=form_del)

@app.route('/borrowman',methods=['GET', 'POST'])
@login_required
def borrowman():
    form_add = forms.BorrowForm()
    form_del = forms.ReturnForm()
    card_info = {}

    if form_add.validate_on_submit() and form_add.submitadd.data:
        card_info = database.borrow_book(form_add,all_table)
    if form_del.validate_on_submit() and form_del.submitdel.data:
        card_info = database.return_book(form_del,all_table)

    return render_template('borrowman.html',
        form_add=form_add,form_del=form_del,card_info = card_info)

@app.route('/cardman',methods=['GET', 'POST'])
@login_required
def cardman():
    form_add = forms.CardAddForm()
    form_del = forms.CardDeleteForm()

    if form_add.validate_on_submit() and form_add.submitadd.data:
        database.card_add(form_add,all_table)
    if form_del.validate_on_submit() and form_del.submitdel.data:
        database.card_del(form_del,all_table)
            
    return render_template('cardman.html',form_add=form_add,form_del=form_del)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/batchimport',methods=['GET', 'POST'])
@login_required
def batch():
    batchform = forms.BatchForm()
    if batchform.validate_on_submit():
        booktable = all_table['book']
        database.book_add_batch(batchform,booktable,app.config["UPLOAD_PATH"])
    return render_template('batchimport.html',batchform=batchform)

if (__name__ == '__main__'):
    global all_table
    app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://oeheart:oyx1234@127.0.0.1:3306/library'
    # 协议：mysql+pymysql
    # 用户名：oeheart
    # 密码：oyx1234
    # IP地址：localhost
    # 端口：3306
    # 数据库名：library
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SECRET_KEY'] = 'getchin?nim'
    app.config['UPLOAD_PATH'] = "./upload"
    Bootstrap(app)
    db.reflect()
    all_table = {table_obj.name: table_obj for table_obj in db.get_tables_for_bind()}   
    login_manager.session_protection = 'basic'
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    app.run(host='127.0.0.1',port=5000)
   