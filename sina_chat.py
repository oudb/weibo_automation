#! /usr/bin/python
# -*- coding: utf-8 -*-
from xvfbwrapper import Xvfb
from splinter import Browser
import time
from selenium.webdriver import DesiredCapabilities

class SinaChat(object):
    """

    """
    vdisplay = None
    login_url = ""
    chat_url = "http://weibo.cn/im/chat?uid=%s"

    def __init__(self, headless=False, driver_name=u'firefox'):
        if headless:
            self.vdisplay = Xvfb()
            self.vdisplay.start()

        if driver_name == u'firefox':
            profile_preferences = {u'permissions.default.stylesheet': 2,
                               u'permissions.default.image': 2,
                               u'dom.ipc.plugins.enabled.libflashplayer.so':
                                      u'false'
            }
            self.browser = Browser(driver_name, profile_preferences=profile_preferences)
        else:
            self.browser = Browser(driver_name,load_images=False,desired_capabilities= DesiredCapabilities.ANDROID.copy())

    def __del__ (self):
        if self.vdisplay is not None:
            self.vdisplay.stop()

    def login(self, user_name, user_password):
        self.browser.visit("http://login.weibo.cn/login/")
        if not self.browser.status_code.is_success():
            print self.browser.status_code
            return False

        self.browser.fill("mobile",user_name)
        self.browser.find_by_xpath('//form/div/input[@type="password"]').first.fill(user_password)
        self.browser.find_by_name("submit").first.click()
        time.sleep(3)
        if self.browser.url.startswith("http://weibo.cn"):
            return True
        else:
            print self.browser.url
            return False

    def login_out(self):
        self.browser.visit(u"http://passport.sina.cn/sso/logout?r=http%3a%2f%2flogin.weibo.cn%2flogin%2f")
        if self.browser.url == "http://login.weibo.cn/login/":
            return True
        else:
            return False

    def send_msg(self, to_uid, content):
        self.browser.visit(self.chat_url % to_uid)
        if not self.browser.status_code.is_success():
            return False
        self.browser.fill("content", content)
        self.browser.find_by_name("send").first.click()
        if self.browser.status_code.code == 302:
            try_count = 0
            ok = None
            while True:
                ok = self.browser.find_by_xpath(u'//div[@class="ps"]')
                if not ok.is_empty()  :
                    break
                elif try_count >= 2:
                    return  False
                else:
                    try_count += 1
                    time.sleep(1)
            if ok.first.text == u"发送成功!":
                return True
            else:
                return False
        else:
            return False


