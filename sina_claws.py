#! /usr/bin/python
# -*- coding: utf-8 -*-
from xvfbwrapper import Xvfb
from splinter import Browser
import math
from collections import deque
import re
import time
from sina_db import SinaData


def _compute_page(total):
    if total >= 100:
        return 5
    else:
        return  int(math.ceil(total / 20.))


class SinaClaws(object):
    """

    """
    follower_path = u'//table[@class="tb_counter"]/tbody/tr/td[2]/a/strong[1]'
    follower_path2 = u'//table[@class="tb_counter"]/tbody/tr/td[2]/strong[1]'
    pattern = re.compile(u"id=(\d+)")
    vdisplay = None

    def __init__(self, headless=False, level=1, db=SinaData()):
        if headless:
            self.vdisplay = Xvfb()
            self.vdisplay.start()
        profile_preferences = {u'permissions.default.stylesheet': 2,
                               u'permissions.default.image': 2,
                               u'dom.ipc.plugins.enabled.libflashplayer.so':
                                      u'false'
        }
        self.browser = Browser(u'firefox', profile_preferences = profile_preferences)
        self.task_queue = deque()
        self.level = level
        self.db = db

    def __del__ (self):
        if self.vdisplay is not None:
            self.vdisplay.stop()

    def login(self, user_name=u"**", user_password=u"**"):
        self.browser.visit(u"http://www.weibo.com/login.php")
        if not self.browser.status_code.is_success():
            return False

        self.browser.find_by_xpath('//div[@class="W_login_form"]/div/div/input[@name="username"]').\
            first.fill(user_name)
        self.browser.find_by_xpath('//div[@class="W_login_form"]/div/div/input[@name="password"]').\
            first.fill(user_password)
        self.browser.find_by_xpath('//div[@class="W_login_form"]/div/div/a[@action-type="btn_submit"] ').\
            first.click()
        time.sleep(3)
        if self.browser.url.find(u"home"):
            return True
        else:
            return False

    def work(self, seed_users):
        """

        """
        for u in seed_users:
            try:
                u_url = u"http://weibo.com/u/%s" % u
                print "try to get fan count:", u_url
                self.browser.visit(u_url)
                try_count = 0
                while True:
                    if not self.browser.find_by_xpath(u'//table[@class="tb_counter"]').is_empty() or try_count >= 5:
                        break
                    print "try again:", u'//table[@class="tb_counter"]'
                    time.sleep(1)
                    try_count += 1

                fan_elm = self.browser.find_by_xpath(self.follower_path)
                if fan_elm.is_empty():
                    fan_elm = self.browser.find_by_xpath(self.follower_path2)
                fan_count = int(fan_elm.first.text)
                self._add_fans_task(u, fan_count, 1)
            except Exception, e:
                print e
                continue
        task_count = 0;
        while len(self.task_queue) > 0:
            task = self.task_queue.popleft()
            task_count += 1
            task_url = task["url"]
            task_type = task["type"]
            try:
                if task_type == "fan":
                    level = task["level"]
                    self._get_fans(task_url, level)
                elif task_type == "user":
                    pass
            except Exception, e:
                print e
                continue
        else:
            print "end in task count:", task_count

    def _add_fans_task(self, uid , fan_count, level = 1):
        for p in xrange(1, _compute_page(fan_count) + 1):
            task_url = "http://weibo.com/%s/fans?page=%s" % (uid, p)
            task = {"url": task_url, "type": "fan", "level":level}
            self.task_queue.append(task)

    def _get_fans(self, url, level):
        print "start to get fans:", url
        self.browser.visit(url)
        try_count = 0
        while True:
            if not self.browser.find_by_xpath('//div[@class="info_from"]').is_empty() or try_count >= 5:
                break
            time.sleep(2)
            try_count += 1

        info_from = self.browser.find_by_xpath('//div[@class="info_from"]/a')
        total_fans = len(info_from)
        if info_from.is_empty():
            print "no fans:", url
            return

        mod_pic = self.browser.find_by_xpath('//dt[@class="mod_pic"]/a')
        fan_cont = self.browser.find_by_xpath('//div[@class="info_connect"]/span[2]/em[@class="count"]/a')

        if total_fans != len(mod_pic) and total_fans != len(fan_cont):
            print "fans info is broken: ", url
            return

        for idx in xrange(0, total_fans):
            try:
                txt = info_from[idx].text.lower()
                if txt.find("iphone") != -1 or txt.find("ipad") != -1:
                    m = self.pattern.search(mod_pic[idx].html)
                    uid = m.group(1)
                    fan_num = int(fan_cont[idx].text)
                    self.db.add_users(uid, fan_num)
                    if level < self.level:
                        self._add_fans_task(uid, fan_num, level + 1)
                else:
                    #print "not target user:", txt
                    pass
            except Exception, e:
                print "can not get fan info:", info_from[idx].text,fan_cont[idx].text ,mod_pic[idx].html,e
                continue






