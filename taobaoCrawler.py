import csv
import sys
import time
import random
import tkinter
from selenium import webdriver
from selenium.webdriver.common.by import By
from threading import Thread
import re
import pandas

f = open('./settings.ini', 'r+')
CONST_KEY_WORD = str(f.readline())
CONST_BEGIN_PAGE = int(f.readline())
CONST_END_PAGE = int(f.readline())
f.close()

# CONST_KEY_WORD = str(input("请输入搜索的商品名称"))
# CONST_BEGIN_PAGE = int(input("请输入起始搜索页面页码"))
# CONST_END_PAGE = int(input("请输入终止搜索页面页码"))

# 全局变量状态文字
gui_text = {}
gui_label_now = {}
gui_label_eta = {}

# 淘宝页面版本 0旧 1新
tbPageVersion = 0


# GUI函数
def guiFunc():
    global gui_text
    global gui_label_now
    global gui_label_eta
    gui = tkinter.Tk()
    gui.title('淘宝搜索页面爬取')
    gui['background'] = '#ffffff'
    gui.geometry("600x100-50+20")
    gui.attributes("-topmost", 1)
    gui_text = tkinter.Label(gui, text='初始化', font=('微软雅黑', '20'))
    gui_text.pack()
    gui_label_now = tkinter.Label(gui, text='暂无信息', font=('微软雅黑', '10'))
    gui_label_now.pack()
    gui_label_eta = tkinter.Label(gui, text='暂无信息', font=('微软雅黑', '10'))
    gui_label_eta.pack()
    gui.mainloop()


# GUI线程控制
Gui_thread = Thread(target=guiFunc, daemon=True)
Gui_thread.start()
time.sleep(2)

# 启动浏览器
keyword = CONST_KEY_WORD
gui_text['background'] = '#ffffff'
gui_text['text'] = '正在启动浏览器'
options = webdriver.ChromeOptions()

options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument("--disable-blink-features")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
browser = webdriver.Chrome(options=options)
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"""
})
browser.get('https://login.taobao.com/member/login.jhtml')
gui_text['background'] = '#ffffff'

# CSV相关
csvfile = open(f'{keyword}_taobao_{time.strftime("%Y-%m-%d_%H-%M", time.localtime())}.csv', 'a', encoding='utf-8-sig',
               newline='')
csvWriter = csv.DictWriter(csvfile,
                           fieldnames=['item_name', 'item_price', 'item_shop', 'shop_link', 'item_link'])
csvWriter.writerow(
    {'item_name': '商品名', 'item_price': '商品价格', 'item_shop': '店铺名称', 'shop_link': '店铺链接',
     'item_link': '商品链接'})

gui_text['text'] = '请尽快手机扫码登录淘宝，10秒后将尝试启动程序'
time.sleep(10)
while browser.title != '我的淘宝':
    gui_text['text'] = '请确保已经登录淘宝，10秒后将再次尝试启动程序'
    time.sleep(10)
# 搜索词与页数获取
gui_text['text'] = '正在操作'
browser.get(f'https://s.taobao.com/search?q={keyword}')
while browser.title == '验证码拦截':
    gui_text['text'] = f'出错：如有滑块验证请及时验证，程序将于验证后重新尝试爬取'
    gui_text['bg'] = 'red'
    gui_label_eta['text'] = '-'
    gui_label_now['text'] = f'-'
    time.sleep(2)
browser.implicitly_wait(10)
try:
    # 老版PC淘宝页面
    taobaoPage = browser.find_element(By.CSS_SELECTOR,
                                      '#J_relative > div.sort-row > div > div.pager > ul > li:nth-child(2)').text
    taobaoPage = re.findall('[^/]*$', taobaoPage)[0]
    tbPageVersion = 0
except:
    # 新版PC淘宝页面
    taobaoPage = browser.find_element(By.CSS_SELECTOR,
                                      '#sortBarWrap > div.SortBar--sortBarWrapTop--VgqKGi6 > div.SortBar--otherSelector--AGGxGw3 > div:nth-child(2) > div.next-pagination.next-small.next-simple.next-no-border > div > span').text
    taobaoPage = re.findall('[^/]*$', taobaoPage)[0]
    tbPageVersion = 1

# 爬取页数控制
gui_text['text'] = '☞等待爬取页数'
gui_text['background'] = '#f35315'
print(f'共计{taobaoPage}页,建议每2小时总计爬取不超过20页')
page_start = int(CONST_BEGIN_PAGE)
page_end = int(CONST_END_PAGE + 1) if int(CONST_END_PAGE + 1) < int(taobaoPage) else int(taobaoPage)
time.sleep(5)
gui_text['background'] = '#ffffff'

for page in range(page_start, page_end):
    gui_text['text'] = f'当前正在获取第{page}页，还有{page_end - page_start - page}页'
    gui_text['bg'] = '#10d269'
    gui_label_now['text'] = '-'
    gui_label_eta['text'] = '-'
    if (tbPageVersion == 0):
        browser.get(
            f'https://s.taobao.com/search?q={keyword}&commend=all&ssid=s5-e&search_type'
            f'=item&sourceId=tb.index&spm=a21bo.jianhua.201856-taobao-item.2&ie=utf8&initiative_id=tbindexz_2017030'
            f'6&&s={(page - 1) * 44} ')
    if (tbPageVersion == 1):
        browser.get(f'https://s.taobao.com/search?q={keyword}&page={page}')
    while browser.title == '验证码拦截':
        gui_text['text'] = f'出错：如有滑块验证请及时验证，程序将于验证后重新尝试爬取'
        gui_text['bg'] = 'red'
        gui_label_eta['text'] = '-'
        gui_label_now['text'] = f'-'
        time.sleep(2)
    # 尝试获取商品列表
    try:
        gui_text['text'] = f'当前正在获取第{page}页，还有{page_end - page_start - page}页'
        gui_text['bg'] = '#10d269'

        if tbPageVersion == 0:
            print('using classic version selector')
            goods_arr = browser.find_elements(By.CSS_SELECTOR, '#mainsrp-itemlist > div > div > div:nth-child(1)>div')
            goods_length = len(goods_arr)
            # 遍历商品
            for i, goods in enumerate(goods_arr):
                gui_label_now['text'] = f'正在获取第{i}个,共计{goods_length}个'
                item_name = goods.find_element(By.CSS_SELECTOR,
                                               'div.ctx-box.J_MouseEneterLeave.J_IconMoreNew > div.row.row-2.title>a').text
                item_price = goods.find_element(By.CSS_SELECTOR,
                                                'div.ctx-box.J_MouseEneterLeave.J_IconMoreNew > div.row.row-1.g-clearfix > div.price.g_price.g_price-highlight > strong').text
                item_shop = goods.find_element(By.CSS_SELECTOR,
                                               'div.ctx-box.J_MouseEneterLeave.J_IconMoreNew > div.row.row-3.g-clearfix > div.shop > a > span:nth-child(2)').text
                shop_link = goods.find_element(By.CSS_SELECTOR,
                                               'div.ctx-box.J_MouseEneterLeave.J_IconMoreNew > div.row.row-3.g-clearfix > div.shop > a').get_attribute(
                    'href')
                item_link = goods.find_element(By.CSS_SELECTOR,
                                               'div.pic-box.J_MouseEneterLeave.J_PicBox > div > div.pic>a').get_attribute(
                    'href')
                try:
                    b = shop_link.split('https://store.taobao.com/shop/view_shop.htm?user_number_id=')[1]
                except:
                    b = shop_link
                csvWriter.writerow(
                    {'item_name': item_name, 'item_price': item_price, 'item_shop': item_shop, 'shop_link': shop_link,
                     'item_link': item_link})
                csvfile.flush()
        if tbPageVersion == 1:
            print('using new version selector')
            goods_arr = browser.find_elements(By.CSS_SELECTOR,
                                              '#root > div > div:nth-child(2) > div.PageContent--contentWrap--mep7AEm > div.LeftLay--leftWrap--xBQipVc > div.LeftLay--leftContent--AMmPNfB > div.Content--content--sgSCZ12 > div>div')
            goods_length = len(goods_arr)
            for i, goods in enumerate(goods_arr):
                i = i + 1
                gui_label_now['text'] = f'正在获取第{i}个,共计{goods_length}个'
                item_name = goods.find_element(By.CSS_SELECTOR,
                                               f'div:nth-child({i})>a>div > div.Card--mainPicAndDesc--wvcDXaK > div.Title--descWrapper--HqxzYq0 > div > span').text
                item_price_int = goods.find_element(By.CSS_SELECTOR,
                                                    f'div:nth-child({i})>a>div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > span.Price--priceInt--ZlsSi_M').text
                item_price_float = goods.find_element(By.CSS_SELECTOR,
                                                      f'div:nth-child({i})>a>div> div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > span.Price--priceFloat--h2RR0RK').text
                item_price = item_price_int + item_price_float
                item_shop = goods.find_element(By.CSS_SELECTOR,
                                               f'div:nth-child({i})>a>div> div.ShopInfo--shopInfo--ORFs6rK  > div>a').text
                shop_link = goods.find_element(By.CSS_SELECTOR,
                                               f'div:nth-child({i})>a>div> div.ShopInfo--shopInfo--ORFs6rK  > div>a').get_attribute(
                    'href')
                item_link = goods.find_element(By.CSS_SELECTOR,
                                               f'div:nth-child({i})>a').get_attribute(
                    'href')
                csvWriter.writerow(
                    {'item_name': item_name, 'item_price': item_price, 'item_shop': item_shop, 'shop_link': shop_link,
                     'item_link': item_link})
                csvfile.flush()
    except:
        # 拉取商品列表失败则提示需要验证
        gui_text['text'] = f'出错：如有滑块验证请及时验证，程序将于20秒后重新尝试爬取'
        gui_text['bg'] = 'red'
        gui_label_eta['text'] = '-'
        gui_label_now['text'] = f'注意:第<{page}>页将跳过如需获取请重新运行程序！'
        print(f'注意:第<{page}>页将跳过如需获取请重新运行程序！')
        time.sleep(20)

    delay_time = random.randint(1, 5)
    for delay in range(delay_time):
        gui_label_now['text'] = '-'
        gui_text['bg'] = '#eeeeee'
        gui_text['text'] = f'第{page}页，还有{page_end - page_start - page}页'
        gui_label_eta['text'] = f'等待下次翻页{delay}秒，总共需等待{delay_time}秒'
        time.sleep(1)

print('程序结束')
gui_text['text'] = '程序结束正在保存文件'
csvfile.close()
gui_text['text'] = '正在导出xlsx'
results_dataframe = pandas.read_csv(csvfile.name)
results_dataframe.to_excel('淘宝爬取商品结果' + f'{time.strftime("%Y-%m-%d_%H-%M", time.localtime())}' + '.xlsx',
                           index=False)
gui_text['text'] = '保存文件完成，准备退出中'
time.sleep(5)
browser.close()
browser.quit()
sys.exit()
