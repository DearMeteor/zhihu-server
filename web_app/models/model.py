# -*- coding: utf-8 -*-
"""
Created by Linjianhui on 2017/1/9
"""
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
    SECRET_KEY = "secret_dc_vip_backend"

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=12000):
        s = Serializer(self.SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(AdminUser.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        # user = AdminUser.query.get(data['id'])
        return data['id']

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    permission = db.Column(db.Text)
    real_name = db.Column(db.String(64))
    is_admin = db.Column(db.Integer)


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    role_id = db.Column(db.String(64))
    app_id = db.Column(db.Integer)
    server_id = db.Column(db.Integer)
    service_id = db.Column(db.Integer)
    account = db.Column(db.String(32))
    vip_lv = db.Column(db.Integer)
    vip_exp = db.Column(db.Integer)
    score = db.Column(db.Integer)

class UserInfo(db.Model):
    __tablename__ = 'user_info'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(32))
    name = db.Column(db.String(32))
    birthdate = db.Column(db.Date)
    phone = db.Column(db.String(16))
    wechat = db.Column(db.String(32))
    qq = db.Column(db.String(16))
    mail = db.Column(db.String(64))
    address = db.Column(db.String(128))
    identity_number = db.Column(db.String(32))


class BannerInfo(db.Model):
    __tablename__ = 'banner_info'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    title = db.Column(db.String(128))
    start_time = db.Column(db.Date)
    end_time = db.Column(db.Date)
    create_time = db.Column(db.DateTime)
    creator = db.Column(db.String(128))
    img_url = db.Column(db.String(256))
    link_url = db.Column(db.String(256))
    status = db.Column(db.Integer)
    style = db.Column(db.String(128))


class GameInfo(db.Model):
    __tablename__ = 'game_info'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    game_name = db.Column(db.String(32))
    game_config = db.Column(db.Text)


class KeyValue(db.Model):
    __tablename__ = 'key_value'

    id = db.Column(db.Integer, primary_key=True)
    s_key = db.Column(db.String(128))
    s_value = db.Column(db.String(128))
    types = db.Column(db.String(128))
    orders = db.Column(db.Integer)


class LoginInfo(db.Model):
    __tablename__ = 'login_info'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    account = db.Column(db.String(64))
    phone = db.Column(db.String(32))
    ip = db.Column(db.String(16))
    last_login_time = db.Column(db.DateTime)


class Portal(db.Model):
    __tablename__ = 'portal'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    portal_name = db.Column(db.String(128))
    link_url = db.Column(db.String(256))
    img_url = db.Column(db.String(256))
    status = db.Column(db.Integer)


class PublishInfo(db.Model):
    __tablename__ = 'publish_info'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    types = db.Column(db.String(64))
    creator = db.Column(db.String(64))
    create_time = db.Column(db.DateTime)
    publish_time = db.Column(db.DateTime)
    status = db.Column(db.Integer)
    style = db.Column(db.String(256))
    orders = db.Column(db.Integer)
    info_prop = db.Column(db.String(256))
    info_type = db.Column(db.String(256))
    is_now = db.Column(db.Integer)
    is_top = db.Column(db.Integer)
    img_url = db.Column(db.String(256))
    section = db.Column(db.String(32))


class AccountStatus(db.Model):
    __tablename__ = 'account_status'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer)
    account = db.Column(db.String(64))
    isFrozen = db.Column(db.Integer)
    isIpBlocked = db.Column(db.Integer)
