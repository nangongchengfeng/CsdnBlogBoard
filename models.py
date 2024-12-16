# -*- coding: utf-8 -*-
# @Time    : 2024/12/15 13:38
# @Author  : 南宫乘风
# @Email   : 1794748404@qq.com
# @File    : models.py.py
# @Software: PyCharm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

db = SQLAlchemy()


class Info(db.Model):
    """
    Model representing the 'info' table
    """
    __tablename__ = 'info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Text)
    head_img = db.Column(db.Text)
    author_name = db.Column(db.Text)
    article_num = db.Column(db.Text)
    fans_num = db.Column(db.Text)
    like_num = db.Column(db.Text)
    comment_num = db.Column(db.Text)
    level = db.Column(db.Text)
    visit_num = db.Column(db.Text)
    score = db.Column(db.Text)
    rank = db.Column(db.Text)


class Categorize(db.Model):
    """
    Model representing the 'categorize' table
    """
    __tablename__ = 'categorize'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    href = db.Column(db.Text)
    categorize = db.Column(db.Text)
    categorize_id = db.Column(db.BigInteger)
    column_num = db.Column(db.BigInteger)
    num_span = db.Column(db.BigInteger)
    article_num = db.Column(db.BigInteger)
    read_num = db.Column(db.BigInteger)
    collect_num = db.Column(db.BigInteger)


class Article(db.Model):
    """
    Model representing the 'article' table
    """
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.Text)
    title = db.Column(db.Text)
    date = db.Column(db.Text)
    read_num = db.Column(db.BigInteger)
    comment_num = db.Column(db.BigInteger)
    type = db.Column(db.Text)
