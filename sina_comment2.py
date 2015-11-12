#! /usr/bin/python
# -*- coding: utf-8 -*-

from splinter.exceptions import ElementDoesNotExist
from xvfbwrapper import Xvfb
from splinter import Browser
import time


class SinaComment(object):
    """

    """
    vdisplay = None

    weibo_url = "http://weibo.com/%s/profile"

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
            #self.browser = Browser(driver_name, profile_preferences=profile_preferences)
            self.browser = Browser(driver_name)
        else:
            self.browser = Browser(driver_name)

    def __del__ (self):
        self.browser.quit()
        if self.vdisplay is not None:
            self.vdisplay.stop()

    def login(self, user_name=u"**", user_password=u"**"):
        self.browser.visit(u"http://www.weibo.com/login.php")
        if not self.browser.status_code.is_success():
            return False

        self.browser.find_by_xpath('//div[@class="W_login_form"]/div/div/input[@name="username"]').\
            first.fill(user_name)

        password = self.browser.find_by_xpath('//div[@class="W_login_form"]/div/div/input[@name="password"]').first
        password.click()
        password.fill(user_password)

        submit = self.browser.find_by_xpath('//div[@class="W_login_form"]/div/a[@action-type="btn_submit"]').first

        for i in xrange(0, 3):
            submit.click()
            time.sleep(5)
            verify_code =  self.browser.find_by_name("verifycode")
            if len(verify_code) == 0:
                break

            if verify_code.visible:
                verify_code_img  = self.browser.find_by_xpath('//img[@node-type="verifycode_image"]').first
                now_time = int(time.time())
                screenshot_name = self.browser.screenshot("%s_%s" % (user_name,  now_time))
                print u"需要验证码", screenshot_name
                verify_code_text = raw_input(u"输入验证码:")
                verify_code.fill(verify_code_text)
                continue

        if self.browser.url.find(u"home") >= 0:
            return True

        return False


    def reload(self):
        """
        Revisits the current URL
        :return:
        """
        self.browser.reload()

    def comment(self, to_uid, content):
        self.browser.visit(self.weibo_url % to_uid)

        #self.browser.visit(self.weibo_url % to_uid)
        if not self.browser.status_code.is_success():
            return False


        comments = self.browser.find_by_xpath('//span[@node-type="comment_btn_text"]')

        if comments.is_empty():
            print u"用户没有微博"
            return True

        wait_time = 1
        try_count = 0
        for comment in comments:
            if try_count >= 3:
                break
            try:
                comment.mouse_over()
                comment.click()
            except Exception, e:
                print u"点击评论按钮失败"
                print e.message
                continue

            try:
                self.browser.find_by_xpath('//div[@class="WB_publish"]/div/textarea').first.fill(content)
                self.browser.find_by_xpath('//div[@class="WB_publish"]/div/div/a[@node-type="btnText"]').first.click()
                if self.browser.is_text_present(u"微博发的太多"):
                    print u"微博发的太多,暂停:", 1800
                    time.sleep(1800)

                return True # 这里就算成功了
            except ElementDoesNotExist,e:
                print e.message
                try_count += 1
                wait_time *= try_count
                print "sleep", wait_time
                time.sleep(wait_time)
            except Exception, e:
                print e.message
        return False


