import sys
import time
import random
import tkinter
from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Thread
import re
import pandas

f = open('./settings.ini', 'r+', encoding='utf8')
CONST_KEY_WORD = str(f.readline().strip())
CONST_BEGIN_PAGE = int(f.readline().strip())
CONST_END_PAGE = int(f.readline().strip())
f.close()

# 全局变量状态文字
gui_text = {}
gui_label_1 = {}
gui_label_2 = {}


def gui_func():
    global gui_text
    global gui_label_1
    global gui_label_2
    gui = tkinter.Tk()
    gui.title('淘宝商品页面爬取')
    gui['background'] = '#ffffff'
    gui.geometry("600x100-50+20")
    gui.attributes("-topmost", 1)
    gui_text = tkinter.Label(gui, text='初始化', font=('微软雅黑', '20'))
    gui_text.pack()
    gui_label_1 = tkinter.Label(gui, text='暂无信息', font=('微软雅黑', '10'))
    gui_label_1.pack()
    gui_label_2 = tkinter.Label(gui, text='暂无信息', font=('微软雅黑', '10'))
    gui_label_2.pack()
    gui.mainloop()


# GUI线程控制
Gui_thread = Thread(target=gui_func, daemon=True)
Gui_thread.start()
time.sleep(2)

# GUI提醒启动浏览器
keyword = CONST_KEY_WORD
gui_text['background'] = '#ffffff'
gui_text['text'] = '正在启动浏览器'

# WebDriver防检测
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(options=options)
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
})

# WebDriver控制打开页面
browser.get('https://login.taobao.com/member/login.jhtml')
browser.maximize_window()

# GUI提醒登录
gui_text['background'] = '#ffffff'
gui_text['text'] = '请尽快扫码登录淘宝，10秒后将尝试自动爬取'
time.sleep(5)
gui_text['text'] = '如有滑块认证请辅助滑块认证'
time.sleep(5)

# 循环检测是否成功登录
while browser.title != '我的淘宝' and browser.title != '淘宝':
    gui_text['text'] = '''请确保已经登录淘宝并在【我的淘宝】页面'''
    gui_text['bg'] = 'red'
    time.sleep(5)
    gui_text['text'] = '''即将重新尝试自动爬取'''

# 输出列表准备
output_list = []


