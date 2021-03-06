#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import threading
import time
from AppiumLibrary import *
from appium import webdriver
from robot import utils
from robot.api import logger
from cfg import *
from launchManagerment import *
from eles.login import *
from eles.minepage import *
from eles.globaleles import *


# set default timeout
TIMEOUT = 15

class AppiumExtend(AppiumLibrary):

    ROBOT_LIBRARY_SCOPE = 'Global'
    localTime = time.strftime("%Y-%m-%d", time.localtime())

    def __init__(self):
        AppiumLibrary.__init__(self)

    # def preInstall(self):
    #     """创建函数用于处理应用安装过程中，处理各种系统弹框问题
    #        bat_path为可执行的用来调用uiautomator脚本的路径
    #     """
    #     p = subprocess.Popen("cmd.exe /c" + bat_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #     curline = p.stdout.readline()
    #     while (curline != b''):
    #         logger.console(curline)
    #         curline = p.stdout.readline()
    #     p.wait()
    #     logger.console(p.returncode)

    def preInstall(self):
        """create function using for dealing with alert during install the app

        """
        watcherpath = getProjectRootPath() + r"\libs\UIWatcher.jar"
        push = subprocess.Popen(
            "adb push " + watcherpath + " data/local/tmp",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        run = subprocess.Popen("adb shell uiautomator runtest UIWatcher.jar -c com.whaleytest.UiWatchers",
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        outter, err = push.communicate()
        outter1, err1 = run.communicate()
        logger.console(outter)
        logger.console(outter1)

    def open_application(self, remote_url, alias=None,**kwargs):
        """Opens a new application to given Appium server.
        Capabilities of appium server, Android and iOS,
        Please check http://appium.io/slate/en/master/?python#appium-server-capabilities
        | *Option*            | *Man.* | *Description*     |
        | remote_url          | Yes    | Appium server url |
        | alias               | no     | alias             |
        Examples:
        | Open Application | http://localhost:4723/wd/hub | alias=Myapp1         | platformName=iOS      | platformVersion=7.0            | deviceName='iPhone Simulator'           | app=your.app                         |
        | Open Application | http://localhost:4723/wd/hub | platformName=Android | platformVersion=4.2.2 | deviceName=192.168.56.101:5555 | app=${CURDIR}/demoapp/OrangeDemoApp.apk | appPackage=com.netease.qa.orangedemo | appActivity=MainActivity |
        """
        preinstallThread = threading.Thread(target=self.preInstall)
        preinstallThread.start()
        desired_caps = kwargs
        application = webdriver.Remote(str(remote_url), desired_caps)
        self._debug('Opened application with session id %s' % application.session_id)

        return self._cache.register(application, alias)



    def jump_to_homepage(self, loginOrnot, remote_servers=remote_server, alias=None, desired_capss=desired_caps, username1='18616512272', password1="a123456"):
        """Opens a new application to given Appium server using defult settings in cfg.py file
           if loginOrnot is True then run login,else open app without login

        Examples:
        |loginApp |${True} |
        |loginApp |${False} |
        |loginApp |${false} |${remote_server} |${desired_capss} |${username} |${password} |
        """
        preinstallThread = threading.Thread(target=self.preInstall)
        preinstallThread.start()
        application = webdriver.Remote(command_executor=remote_servers,desired_capabilities=desired_capss)
        while loginOrnot:
            application.find_element_by_id(loginbutton).click()
            application.find_element_by_id(username).send_keys(username1)
            application.find_element_by_id(password).send_keys(password1)
            time.sleep(1)
            application.find_element_by_id(loginbutton).click()
            break

        application.find_element_by_id(leapfrog).click()

        self._debug('Opened application with session id %s' % application.session_id)
        return self._cache.register(application, alias)

    def back_to_homepage(self,message="",timeout=TIMEOUT):
        """click backbutton go back to homepage using for setup or treadown test

        Example:
        | back to homepage |
        """
        locator = "id=" + backbutton
        while self.is_element_present(locator):
            self._wait_until_no_error_fixed(timeout,True,message,self.click_element,locator)

    def click_back_nth(self,nth,message="",timeout=TIMEOUT):
        """click backbutton nth times
        :param nth:
        :param message:
        :param timeout:
        :return:
        Example:
        | click back nth | 2 |

        """
        locator = "id=" + backbutton
        for one in range(nth):
            self._wait_until_no_error_fixed(timeout,True,message,self.click_element,locator)


    def swith_to_debug_mode(self):
        """swith the app to debug mode

        """
        self.back_to_homepage()
        self.wait_until_element_is_visible("id="+mybase,10)
        self.click_element("id="+mybase)
        self.click_element("id="+settingbutton)
        debugbutton = "id="+debugswith
        debug = self.get_text("id=com.snailvr.manager:id/tv_debug")
        if debug == u'是':
            self.back_to_homepage()
        else:
            self.click_element(debugbutton)
            self.go_back()
            self.go_back()
            self.go_back()
            cmd = "adb shell am start -n com.snailvr.manager/com.whaley.vr.module.launcher.activitys.SplashActivity"
            subprocess.Popen(cmd,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        self._wait_until_no_error_fixed(timeout,True,message,self.page_should_contain_element,"id="+mybase)

    def jump_to_homepage_and_swith_to_debug_mode(self,loginOrnot):
        """login app adn swith app to debugmode
        if loginOrnot is False,then swith app to debugmode without login

        Examples:
        | login and swith to debug mode | ${False} |
        | login and swith to debug mode | ${True} |
        """
        self.jump_to_homepage(loginOrnot)
        self.swith_to_debug_mode()
        locator = "id="+leapfrog
        time.sleep(3)
        while not loginOrnot:
            # self._wait_until_no_error_fixed(timeout,True,message,self.click_element,locator)
            self.click_element(locator)
            break


    def getsize(self):
        """get the max X,Y coordinate of srceen

        """
        x = self._current_application().get_window_size()['width']
        y = self._current_application().get_window_size()['height']
        return x,y

    def swipe_up_nth(self,nth=1):
        """swipe the screen up nth times

        Exapmles:
        | swipe up nth |
        | swipe up nth | 2 |
        """
        size = self.getsize()
        x1 = int(size[0]*0.5)
        y1 = int(size[1]*0.75)
        y2 = int(size[1]*0.25)
        nth = int(nth)
        for one in range(nth):
            self._current_application().swipe(x1,y1,x1,y2,1000)
            time.sleep(1)

    def swipe_down_nth(self,nth=1):
        """swipe the screen down nth times

        Exapmles:
        | swipe dowm nth |
        | swipe woen nth | 2 |
        """
        size = self.getsize()
        x1 = int(size[0]*0.5)
        y1 = int(size[1]*0.25)
        y2 = int(size[1]*0.75)
        nth = int(nth)
        for one in range(nth):
            self._current_application().swipe(x1,y1,x1,y2,1000)
            time.sleep(1)

    def swipe_left_nth(self,nth=1):
        """swipe the screen left nth times
        Exapmles:
        | swipe left nth |
        | swipe left nth | 2 |
        """
        size = self.getsize()
        x1 = int(size[0]*0.75)
        y1 = int(size[1]*0.5)
        x2 = int(size[0]*0.05)
        nth = int(nth)
        for one in range(nth):
            self._current_application().swipe(x1,y1,x2,y1,1000)
            time.sleep(1)

    def swipe_right_nth(self,nth=1):
        """swipe the screen right nth times
        Exapmles:
        | swipe right nth |
        | swipe right nth | 2 |
        """
        size = self.getsize()
        x1 = int(size[0]*0.05)
        y1 = int(size[1]*0.5)
        x2 = int(size[0]*0.75)
        nth = int(nth)
        for one in range(nth):
            self._current_application().swipe(x1,y1,x2,y1,1000)
            time.sleep(1)

    def input_until_no_error(self, locator, text, message="", timeout=TIMEOUT):
        """Try types the given `text` into text field identified by `locator` until no error occurred.

        Fails if `timeout` expires before the input success.

        Examples:
        | Input Until No Error | class=android.widget.Button | username |                |     |
        | Input Until No Error | class=android.widget.Button | username | input username | 10s |
        """
        if not message:
            message = "Typing text '%s' into text field '%s'" % (text, locator)
        self._wait_until_no_error_fixed(timeout, True, message, self.input_text, locator, text)

    def clear_until_no_error(self, locator, message="", timeout=TIMEOUT):
        """Try clear `text` in text field identified by `locator` until no error occurred.

        Fails if `timeout` expires before the clear success.

        Examples:
        | Clear Until No Error |               |                |     |
        | Clear Until No Error | name=username | clear username | 10s |
        """
        if not message:
            message = "Clear text field '%s'" % locator
        self._wait_until_no_error_fixed(timeout, True, message, self.clear_text, locator)

    def click_element_until_no_error(self, locator, message="", timeout=TIMEOUT):
        """Try click element identified by `locator` until no error occurred.

        Fails if `timeout` expires before the click success.

        Examples:
        | Click Until No Error | name=Login |           |     |
        | Click Until No Error | name=Login | click btn | 10s |
        """
        if not message:
            message = "Clicking element '%s'" % locator
        self._wait_until_no_error_fixed(timeout, True, message, self.click_element, locator)

    def click_nth_element(self, locator, nth=1):
        """Click the nth element identified by `locator`.

        Examples:
        | #Click the 2th element |                             |    |
        | Click Nth Element      | class=android.widget.Button |  2 |
        | #Click last element    |                             |    |
        | Click Nth Element      | class=android.widget.Button | -1 |
        """
        try:
            nth = int(nth)
        except ValueError, e:
            raise ValueError(u"'%s' is not a number" % nth)
        if nth == 0:
            raise ValueError(u"'nth' must not equal 0")
        elements = self.get_webelements(locator)
        self._info("Clicking %dth element '%s'" % (nth, locator))
        if nth > 0:
            elements[nth - 1].click()
        elif nth < 0:
            elements[nth].click()

    def click_nth_element_until_no_error(self, locator, nth=1, message="", timeout=TIMEOUT):
        """Click the nth element identified by `locator` until no error occurred.

        Fails if `timeout` expires before the click success.

        Examples:
        | #Click the 2th element   |                             |    |                |     |
        | Click Nth Until No Error | class=android.widget.Button |  2 |                |     |
        | #Click last element      |                             |    |                |     |
        | Click Nth Until No Error | class=android.widget.Button | -1 | click last btn | 10s |
        """
        if not message:
            message = "Clicking %sth element '%s'" % (nth, locator)
        self._wait_until_no_error_fixed(timeout, True, message, self.click_nth_element, locator, nth)


    # def click_element_until_exists(self, locator,message="",timeout=TIMEOUT):
    #
    #
    #     if not message:
    #         message = "Clicking element '%s' until element '%s' appear" % locator
    #
    #     if self.is_element_present(locator):
    #         self.click_element(locator)

    def click_until_waitElement_exists(self, locator, wait_locator, message="", timeout=TIMEOUT):
        """Click element identified by `locator` until element identified by `wait_locator` appear.

        Fails if `timeout` expires before element identified by `wait_locator` appear.

        Examples:
        | Click Until Element Exists | name=first | name=twice |                                    |     |
        | Click Until Element Exists | name=first | name=twice | Click 'first' until 'twice' appear | 10s |
        """
        if not message:
            message = "Clicking element '%s' until element '%s' appear" % (locator, wait_locator)

        def click_if_not_exists():
            try:
                self.click_element(locator)
            except Exception:
                raise "cannot find element by '%s' or '%s' is not present"%(locator,wait_locator)
            self.page_should_contain_element(wait_locator)

        self._wait_until_no_error_fixed(timeout, True, message, click_if_not_exists)

    def click_nth_element_until_waitelement_exists(self, locator, nth, wait_locator, message="", timeout=TIMEOUT):
        """Click the nth element identified by `locator` until element identified by `wait_locator` appear.

        Fails if `timeout` expires before element identified by `wait_locator` appear.

        Examples:
        | Click Nth Until Element Exists | name=test1 |  2 | name=test2 |                                         |     |
        | Click Nth Until Element Exists | name=test1 | -1 | name=test2 | Click last 'test1' until 'test2' appear | 10s |
        """
        if not message:
            message = "Clicking %sth element '%s' until element '%s' appear" % (nth, locator, wait_locator)

        def click_nth_if_not_exists():
            try:
                self.click_nth_element(locator, nth)
            except Exception as e:
                raise e
            self.page_should_contain_element(wait_locator)

        self._wait_until_no_error_fixed(timeout, True, message, click_nth_if_not_exists)

    def scroll_continue_no_error(self, locator_list, message=""):
        """Scrolls from one element to another.

        Do not raise error if any step failed.

        Examples
        | Scroll Continue No Error | name=first,name=twice,name=third |                            |
        | Scroll Continue No Error | name=first,name=twice,name=third | Scroll first->twice->third |
        """
        if not isinstance(locator_list, list):
            _locator_list = self._convert_to_list(locator_list)
        if not message:
            message = "Scrolling [%s]" % ("->".join(_locator_list))
        flag = True
        for index in range(len(_locator_list) - 1, 0, -1):
            try:
                self.scroll(_locator_list[index - 1], _locator_list[index])
            except:
                flag = False
                continue
        if flag:
            self._info(u"%s ==> PASS." % (message))
        else:
            self._info(u"%s ==> NOT ALL PASS." % (message))

    def click_if_exists_in_time(self, locator, message="", timeout=TIMEOUT):
        """Try click element identified by `locator` in setting time.

        Ignore if `timeout` expires before the click success.

        Examples:
        | Click If Exists In Time | name=skip |                                    |     |
        | Click If Exists In Time | name=skip | click skip, no error if click fail | 10s |
        """
        if not message:
            message = "Clicking element '%s'" % locator
        return self._wait_until_no_error_fixed(timeout, False, message, self.click_element, locator)

    def double_click_element(self, locator):
        """Try double click element identified by 'locator'

        Examples:
        | Double click element | name=login |
        """

        try:
            self.click_element(locator)
            time.sleep(1)
            self.click_element(locator)
        except Exception:
            raise "element cannot found by '%s'" %locator

    def double_click_until_no_error(self, locator, message="", timeout=TIMEOUT):
        """Try double click element identified by `locator` until no error occurred.

        Fails if `timeout` expires before the click success.

        Examples:
        | Double Click Until No Error | name=Login |                         |     |
        | Double Click Until No Error | name=Login | double click login link | 10s |
        """

        if not message:
            message = "Double clicking element '%s'" % locator
        self._wait_until_no_error_fixed(timeout, True, message, self.double_click_element(locator), locator)



    def is_element_present(self, locator):
        """Check the element identified by `locator` is exist or not.

        Return True if locator element present, False if locator element not present.

        Examples:
        | ${isPresent}= | Is Element Present | name=Login |
        """
        return self._is_element_present(locator)

    def get_element_attribute_in_time(self, locator, attribute, message="", timeout=TIMEOUT):
        """Get element attribute using given attribute: name, value,... by `locator` until no error occurred.

        Fails if `timeout` expires before the click success.

        Examples:
        | Get Element Attribute In Time | id=com.xx/id/what | text |                  |     |
        | Get Element Attribute In Time | id=com.xx/id/what | text | get element name | 10s |
        """
        if not message:
            message = "Element locator '%s' did not match any elements." % locator
        return self._wait_until_no_error_fixed(timeout, True, message, self.get_element_attribute, locator, attribute)

    def get_element_count(self, locator, fail_on_error=True):
        """Count elements found by `locator`.

        Examples:
        | ${count}= | Get Element Count | class=android.widget.Button |
        """
        return len(self.get_elements(locator, fail_on_error=fail_on_error))

    def get_element_count_in_time(self, locator, message="", timeout=TIMEOUT):
        """Count elements found by `locator` until result is not 0.

        Return 0 if `timeout` expires.

        Examples:
        | ${count}= | Get Element Count In Time | class=android.widget.Button |              |     |
        | ${count}= | Get Element Count In Time | class=android.widget.Button | count button | 10s |
        """
        return self._wait_until_not_value(timeout, 0, False, message, self.get_element_count, locator)

    def page_should_contain_text_in_time(self, text, message="", timeout=TIMEOUT):
        """Verifies text is not found on the current page in setting time.

        Fails if `timeout` expires before find page contain text.

        Examples:
        | Page Should Contain Text In Time | hello world |            |     |
        | Page Should Contain Text In Time | hello world | check page | 10s |
        """
        if not message:
            message = "Page should have contained text '%s' in %s" % (text, self._format_timeout(timeout))
        self._wait_until_no_error_fixed(timeout, True, message, self.page_should_contain, text, 'NONE')

    def page_should_contain_element_in_time(self, locator, message="", timeout=TIMEOUT):
        """Verifies element identified by `locator` is not found on the current page in setting time.

        Fails if `timeout` expires before find page contain locator element.

        Examples:
        | Page Should Contain Element In Time | name=Login |                          |     |
        | Page Should Contain Element In Time | name=Login | check login button exist | 10s |
        """
        if not message:
            message = "Page should have contained element '%s' in %s" % (locator, self._format_timeout(timeout))
        self._wait_until_no_error_fixed(timeout, True, message, self.page_should_contain_element, locator, 'NONE')

    def wait_until_page_contains_elements(self, locator_list, message="", timeout=TIMEOUT):
        """Waits until any element specified with `locator_list` appears on current page.

        Return appear locator if found.
        Fails if `timeout` expires before the element appears.

        Examples:
        | Wait Until Page Contains Elements | name=unlogin, name=login          |                            |                       |     |
        | ${appear_locator}=                | Wait Until Page Contains Elements | [name=unlogin, name=login] | wait elements appears | 10s |
        """
        if not isinstance(locator_list, list):
            _locator_list = self._convert_to_list(locator_list)
        message_info = "Wait Page contains %s in %s" % (
        " or ".join(["'" + i + "'" for i in _locator_list]), self._format_timeout(timeout))
        if not message:
            message = message_info
        self._info(u"%s." % message_info)
        timeout = utils.timestr_to_secs(timeout) if timeout is not None else 15
        maxtime = time.time() + timeout
        while True:
            for locator in _locator_list:
                if self._is_element_present(locator):
                    self._info(u"%s ==> PASS." % message)
                    return locator
                else:
                    if time.time() > maxtime:
                        raise AssertionError(u"%s ==> FAIL." % message)

                continue
            break

    def _convert_to_list(self, str_list):
        if str_list.startswith('[') and str_list.endswith(']'):
            str_list = str_list[1:-1]
        return [i.strip() for i in str_list.split(',')]

    def _wait_until_no_error_fixed(self, timeout, fail_raise_error, message, wait_func, *args):
        timeout = utils.timestr_to_secs(timeout) if timeout is not None else 15
        maxtime = time.time() + timeout
        while True:
            try:
                res = wait_func(*args)
            except:
                timeout_error = True
            else:
                timeout_error = False
            if not timeout_error:
                self._info(u"%s ==> PASS." % message)
                return res
            if time.time() > maxtime:
                if not fail_raise_error:
                    self._info(u"%s ==> NOT PASS." % message)
                    return False
                else:
                    raise AssertionError(u"%s ==> FAIL." % message)
            break

    def _wait_until_not_value(self, timeout, value, fail_raise_error, message, wait_func, *args):
        timeout = utils.timestr_to_secs(timeout) if timeout is not None else 20
        maxtime = time.time() + timeout
        while True:
            res = wait_func(*args)
            if res != value:
                if message:
                    self._info(u"%s ==> %s." % (message, res))
                return res
            if time.time() > maxtime:
                if not fail_raise_error:
                    if message:
                        self._info(u"%s ==> %s." % (message, res))
                    return res
                if message:
                    raise AssertionError(u"%s ==> %s." % (message, res))
                else:
                    raise AssertionError(u"Return ==> %s." % res)
                break
            time.sleep(0.5)

