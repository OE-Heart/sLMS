from main import db
from flask import flash
from flask_login import current_user
import time
import os
import decimal

def book_search(form,book_table):
    # 传入表单，返回查询结果
    filt = db.session.query(book_table)
    if (form.category.data):
        filt = filt.filter_by(category=form.category.data)
    if (form.title.data):
        filt = filt.filter_by(title=form.title.data)
    if (form.author.data):
        filt = filt.filter_by(author=form.author.data)
    if (form.press.data):
        filt = filt.filter_by(press=form.press.data)
    if (form.year.data):
        filt = filt.filter_by(year=form.year.data)
    result = filt.all()
    return result

def book_add(form_add,all_table):
    # 增加，看书是不是已经存在，不存在增加书目，存在更新数量和库存
    booktable = all_table['book']

    result =db.session.query(booktable).filter_by(BID=form_add.BID.data)
    if (result.first() is None):
        insert = booktable.insert().values(
            BID = form_add.BID.data,
            category = form_add.category.data,
            title = form_add.title.data,
            total = form_add.total.data,
            stock = form_add.stock.data,
            press = form_add.press.data,
            year = form_add.year.data,
            author = form_add.author.data,
            price = form_add.price.data
        )
        db.session.execute(insert)
        flash("添加成功")
    else:
        update = booktable.update().where(
            booktable.c.BID == form_add.BID.data
        ).values(
            total = result.first()['total']+form_add.total.data,
            stock = result.first()['stock']+form_add.total.data
        )
        db.session.execute(update)
        flash("这本书已经存在，增加库存")
    db.session.commit()

def book_delete(form_del,all_table):
    # 删除，看书是不是存在，不存在报错
    #   如果存在 1.删除对应的借书记录(待测试) 2.删除书目
    booktable = all_table['book']
    recordtable = all_table['record']

    result =db.session.query(booktable).filter_by(BID=form_del.BID.data)
    if (result.first() is not None):
        borrow_result = db.session.query(recordtable).filter_by(BID=form_del.BID.data)
        borrow_result.delete()
        result.delete()
        db.session.commit()
        flash("删除成功")
    else:
        flash("删除失败，该书号不存在")

def borrow_book(form_add,all_table):
    # 借书 卡+书号
    # 如果没卡，报错;
    # 如果有卡，显示卡的所有借阅信息
    #   书没了，报错
    #   有书，借书，输出最后归还时间
    recordtable = all_table['record']
    booktable = all_table['book']
    cardtable = all_table['card']
    card_info = {}

    CID = form_add.CID.data
    if (db.session.query(cardtable).filter_by(CID = CID).first() is not None):
        bookid = form_add.BID.data
        card_info = card_search(CID,all_table)
        book = db.session.query(booktable).filter_by(BID = bookid).first()
        if (book is not None):
            if (book['stock']>0):
                update = booktable.update().where(
                    booktable.c.BID == bookid
                ).values(
                    stock = book['stock']-1,
                )
                insert = recordtable.insert().values(
                    RID = 9999999999 if db.session.query(recordtable).first() is None else int(db.session.query(recordtable).first().RID)-1,
                    BID = book['BID'],
                    CID = CID,
                    AID = current_user.AID,
                    borrow_date = time.strftime("%Y-%m-%d",time.localtime(time.time())),
                    return_date = None
                )
                db.session.execute(update)
                db.session.execute(insert)
                db.session.commit()
                card_info = card_search(CID,all_table)
                flash("借阅成功")
            else:
                books = db.session.query(recordtable).filter_by(BID = bookid).order_by(recordtable.c.return_date.desc()).all()
                for book in books:
                    if book['return_date'] is not None:
                        break
                flash("借阅失败，该书已无库存")
        else:
            flash("借阅失败，该书号不存在")
    else:
        flash("借阅失败，该卡号不存在")
    return card_info


def return_book(form_del,all_table):
    # 还书
    # 如果没卡，报错;
    # 如果有卡，显示卡的所有借阅信息
    #   如果在borrow里，还书， stock+1, return_date
    #   如果不再，报错
    recordtable = all_table['record']
    booktable = all_table['book']
    cardtable = all_table['card']
    card_info = {}

    CID = form_del.CID.data
    if (db.session.query(cardtable).filter_by(CID = CID).first() is not None):
        bookid = form_del.BID.data
        card_info = card_search(CID,all_table)
        book = db.session.query(recordtable).filter_by(BID = bookid,CID=CID,AID=current_user.AID,return_date = None).first()
        if (book is not None):
            stock = db.session.query(booktable).filter_by(BID = bookid).first()['stock']
            update1 = booktable.update().where(
                booktable.c.BID == bookid
            ).values(
                stock = stock+1,
            )
            update2 = recordtable.update().where(
                recordtable.c.BID == bookid,
                recordtable.c.CID == CID,
                recordtable.c.AID == current_user.AID
            ).values(
                return_date = time.strftime("%Y-%m-%d",time.localtime(time.time()))
            )
            db.session.execute(update1)
            db.session.commit()
            db.session.execute(update2)
            db.session.commit()
            card_info = card_search(CID,all_table)
            flash("归还成功")
        else:
            flash("归还失败，该书号不存在")
    else:
        flash("归还失败，该卡号不存在")
    return card_info

def book_add_batch(form,booktable,upload_path):
    batch_file = form.file.data
    batch_file.save(os.path.join(upload_path,"batch.txt"))

    with open("./upload/batch.txt") as fileobj:
        lines = fileobj.readlines()
        for line in lines:
            line = line.strip().split(';')
            insert = booktable.insert().values(
                BID = line[0],
                category = line[1],
                title = line[2],
                press = line[3],
                year = line[4],
                author = line[5],
                price = None if line[6] is None else decimal.Decimal(line[6]),
                total = int(line[7]),
                stock = int(line[7])
            )
            try:
                db.session.execute(insert)
                db.session.commit()
            except:
                pass
    flash(f"批量入库成功")

def card_search(CID,all_table):
    recordtable = all_table['record']
    booktable = all_table['book']
    book_list = []
    borrow_info = db.session.query(recordtable).filter_by(CID = CID).all()
    for borrowitem in borrow_info:
        book_list.append(db.session.query(booktable).filter_by(BID = borrowitem['BID']).first())
    return book_list

def card_add(form_add,all_table):
    # 添加  如果已经存在，报错;不存在把所有信息insert
    cardtable = all_table['card']

    result = db.session.query(cardtable).filter_by(CID=form_add.CID.data)
    if (result.first() is None):
        insert = cardtable.insert().values(
            CID = form_add.CID.data,
            name = form_add.name.data,
            department = form_add.department.data,
            type = form_add.type.data
        )
        db.session.execute(insert)
        db.session.commit()
        flash("添加成功")
    else:
        flash("添加失败，该卡号已经存在")

def card_del(form_del,all_table):
    # 删除  如果存在未还的书，禁止删除; 否则删除
    cardtable = all_table['card']
    recordtable = all_table['record']
    
    result = db.session.query(cardtable).filter_by(CID = form_del.CID.data)
    if (result.first() is not None):
        recordinfo = db.session.query(recordtable).filter_by(CID = form_del.CID.data).all()
        can_be_delete = True
        for i in recordinfo:
            if (i['return_date'] is None):
                can_be_delete = False
                break
        if can_be_delete:
            result.delete()
            db.session.commit()
            flash("删除成功")            
        else:
            flash("删除失败，存在未归还图书")            
    else:
        flash("删除失败，该卡号不存在")


