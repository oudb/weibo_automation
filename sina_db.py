#! /usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import time

class SinaData(object):

    add_users_sql = u"insert into user(uid, fan_count, add_time) values (?, ?, ?)"
    def __init__(self, db_path = u"sina.db"):
        self.db = sqlite3.connect(db_path)

    def add_users(self, uid, fan_count):
        try:
            with self.db:
                self.db.execute(self.add_users_sql, (uid, fan_count, time.time()))
        except sqlite3.IntegrityError:
            print u"user has exist", uid

    def get_seed_users(self):
        crs = self.db.execute(u"select uid, nick from seed_user")
        res = []
        for row in crs.fetchall():
            print u"add seed user:", row[0], row[1]
            res.append(row[0])
        return res


    def get_users(self, count=50):
        crs = self.db.execute(u"select max(last_time) from log")
        last_time, = crs.fetchone()
        if last_time is None:
            last_time = 0
        crs = self.db.execute(u"select uid,add_time from user where add_time > ? order by  add_time asc limit ?",
                              (last_time, count))


        res =[]
        max_last_time = 0.
        for row in crs.fetchall():
            res.append(row[0])
            max_last_time = row[1]
        if len(res) == 0:
            return res

        self.db.execute(u"insert into log(last_time, finsh_time) values (?,?)", (max_last_time, time.time()))
        self.db.commit()
        return res

    def get_chat_user(self):
        crs = self.db.execute(u"select name, password from chat_user")
        return [(row[0], row[1]) for row in crs.fetchall()]


