# -*- coding: utf-8 -*-
from datetime import datetime, time, date

from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

db = SQLAlchemy()


def to_dict(self, filters=()):
    data = {}
    for c in self.__table__.columns:
        if c.name not in filters:
            value = getattr(self, c.name, None)
            if isinstance(value, datetime) or isinstance(value, time) or isinstance(value, date):
                data[c.name] = str(value)
            else:
                data[c.name] = value
    return data


# 将字典格式化方法设置到db.Model基类上
db.Model.to_dict = to_dict
db.Model.__str__ = lambda self: str(self.to_dict())
db.Model.__repr__ = lambda self: repr(self.to_dict())


def execute_bind(sql, bind=None, **kw):
    return db.session.execute(sql, bind=db.get_engine(db.get_app(), bind=bind), **kw)


db.execute_bind = execute_bind


class AdminUser(db.Model):
    __tablename__ = 'admin_user'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    permission = db.Column(db.Text)
    real_name = db.Column(db.String(64))
    is_admin = db.Column(db.Integer)


class AnswerInfo(db.Model):
    __tablename__ = 'answer_info'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer)
    answer_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    identify_num = db.Column(db.Integer)
    comment_num = db.Column(db.Integer)


class QuestionInfo(db.Model):
    __tablename__ = 'question_info'

    question_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    answer_num = db.Column(db.Integer)
    content = db.Column(db.Text)


class UserInfo(db.Model):
    __tablename__ = 'user_info'

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64))
    content = db.Column(db.Text)
    icon = db.Column(db.String(64))