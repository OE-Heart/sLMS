from flask_wtf import FlaskForm
from wtforms import BooleanField,StringField,IntegerField,DecimalField,SubmitField\
    ,RadioField,DateField,SelectField,PasswordField,FileField
from wtforms.validators import DataRequired, Required,AnyOf,Optional

class LoginForm(FlaskForm):
    """登录表单类"""
    name = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    
    submit = SubmitField("登录")

class BookQueryForm(FlaskForm):
    category = StringField('类别')
    title = StringField('书名')
    press = StringField('出版社')
    year = IntegerField('出版年份', validators=[Optional()])
    author = StringField('作者')
    price = DecimalField('价格', validators=[Optional()])
    submit = SubmitField("搜索")

class CardAddForm(FlaskForm):
    CID = StringField('卡号', validators=[Required()])
    name = StringField('姓名', validators=[Required()])
    department = StringField('单位', validators=[Required()])
    type = SelectField('持卡人类别',choices=['T','S'])

    submitadd = SubmitField("添加")

class CardDeleteForm(FlaskForm):
    CID = StringField('卡号', validators=[Required()])
    
    submitdel = SubmitField("删除")

class BorrowForm(FlaskForm):
    CID = StringField('卡号', validators=[Required()])
    BID = StringField('书号', validators=[Required()])
    
    submitadd = SubmitField("借阅")

class ReturnForm(FlaskForm):
    CID = StringField('卡号', validators=[Required()])
    BID = StringField('书号', validators=[Required()])
    
    submitdel = SubmitField("归还")

class BookAddForm(FlaskForm):
    BID = StringField('书号', validators=[Required()])
    category = StringField('类别', validators=[Required()])
    title = StringField('书名', validators=[Required()])
    press = StringField('出版社')
    year = IntegerField('出版年份', validators=[Optional()])
    author = StringField('作者')
    price = DecimalField('价格',validators=[Optional()] )
    total = IntegerField('总藏书量', validators=[Required()])
    stock = IntegerField('目前库存量', validators=[Required()])
    
    submitadd = SubmitField("添加")

class BookDeleteForm(FlaskForm):
    BID = StringField('书号', validators=[Required()])

    submitdel = SubmitField("删除")

class BatchForm(FlaskForm):
    file = FileField("选择上传文件", validators=[Required()])

    submit = SubmitField("上传")