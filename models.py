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
    # 基础用户信息
    head_img = db.Column(db.Text) # 头像链接
    author_name = db.Column(db.Text) # 作者姓名
    code_age = db.Column(db.Text) # 码龄 (如 "码龄7年")

    # 统计数据 (这些字段在保存前需要将抓取的字符串数字转换为整数)
    article_num = db.Column(db.Text) # 原创文章数 (原Text -> Integer)
    fans_num = db.Column(db.Text) # 粉丝数 (原Text -> Integer)
    like_num = db.Column(db.Text) # 点赞数 (原Text -> Integer)
    comment_num = db.Column(db.Text) # 评论数 (原Text -> Integer)
    collect_num = db.Column(db.Text) # 收藏数 (新字段 -> Integer)
    share_num = db.Column(db.Text) # 分享数 (新字段 -> Integer)
    visit_num = db.Column(db.Text) # 总访问量 (原Text -> Integer)
    rank = db.Column(db.Text) # 排名 (原Text -> Integer)

    level = db.Column(db.Text)  # 等级
    score = db.Column(db.Text) # 原来是 Text，改为 Integer 更合理

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
