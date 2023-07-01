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
def gui_func():
    global gui_text
    global gui_label_now
    global gui_label_eta
    gui = tkinter.Tk()
    gui.title('淘宝搜索页面爬取---号外电商')
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
while browser.title != '我的淘宝':
    gui_text['text'] = '''请确保已经登录淘宝并在【我的淘宝】页面'''
    gui_text['bg'] = 'red'
    time.sleep(5)
    gui_text['text'] = '''即将重新尝试自动爬取'''

# 搜索词与页数管理
gui_text['text'] = '正在操作'
gui_text['background'] = '#ffffff'
browser.get(f'https://s.taobao.com/search?q={keyword}')
# GUI提醒：验证码拦截
while browser.title == '验证码拦截':
    gui_text['text'] = f'出错：如有滑块验证请及时验证，程序将于验证后重新尝试爬取'
    gui_text['bg'] = 'red'
    gui_label_eta['text'] = '-'
    gui_label_now['text'] = f'-'
    time.sleep(2)
browser.implicitly_wait(5)
gui_text['text'] = f'等待完全加载页面中'
gui_text['background'] = '#f35315'

# 检测淘宝新老搜索页面
try:
    # 老版PC淘宝页面
    taobaoPage = browser.find_element(By.CSS_SELECTOR,
                                      '#J_relative > div.sort-row > div > div.pager > ul > li:nth-child(2)').text
    taobaoPage = re.findall('[^/]*$', taobaoPage)[0]
    tbPageVersion = 0

except:
    # 新版PC淘宝页面
    taobaoPage = browser.find_element(By.CSS_SELECTOR,
                                      '#sortBarWrap > div.SortBar--sortBarWrapTop--VgqKGi6 > '
                                      'div.SortBar--otherSelector--AGGxGw3 > div:nth-child(2) > '
                                      'div.next-pagination.next-small.next-simple.next-no-border > div > span').text
    taobaoPage = re.findall('[^/]*$', taobaoPage)[0]
    tbPageVersion = 1
    sale_desc_button = browser.find_element(By.CSS_SELECTOR,
                                            '#sortBarWrap > div.SortBar--sortBarWrapTop--VgqKGi6 > div:nth-child(1) > div > div.next-tabs-bar.SortBar--customTab--OpWQmfy > div > div > div > ul > li:nth-child(2)')
    sale_desc_button.click()

# GUI提醒页面
gui_text['text'] = f'目录检测到共计{taobaoPage}页'
gui_text['background'] = '#f35315'
time.sleep(2)

# 页数控制
page_start = int(CONST_BEGIN_PAGE)
page_end = int(CONST_END_PAGE + 1) if int(CONST_END_PAGE + 1) < int(taobaoPage) else int(taobaoPage)

# GUI提醒页面
gui_text['text'] = f'将从{page_start}页爬取到{page_end - 1}页'
gui_text['background'] = '#ffffff'
time.sleep(2)

# 输出列表准备
output_list = []

# 循环爬取程序
for page in range(page_start, page_end):
    gui_text['text'] = f'当前正在获取第{page}页，还有{page_end - page_start - page}页'
    gui_text['bg'] = '#10d269'
    gui_label_now['text'] = '暂无数据'
    gui_label_eta['text'] = '暂无数据'

    # 判断淘宝搜索页面版本
    if tbPageVersion == 0:
        browser.get(
            f'https://s.taobao.com/search?_input_charset=utf-8&commend=all&ie=utf8&page=3&q={keyword}&search_type=item&source=suggest&sourceId=tb.index&spm=a21bo.jianhua.201856-taobao-item.2&ssid=s5-e&suggest=history_1&suggest_query=&wq=&sort=sale-desc&s={(page - 1) * 44} ')
    elif tbPageVersion == 1:
        if page != page_start:
            next_page_button = browser.find_element(By.CSS_SELECTOR,
                                                    '#sortBarWrap > div.SortBar--sortBarWrapTop--VgqKGi6 > div.SortBar--otherSelector--AGGxGw3 > div:nth-child(2) > div.next-pagination.next-small.next-simple.next-no-border > div > button.next-btn.next-small.next-btn-normal.next-pagination-item.next-next')
            next_page_button.click()
        # browser.get(f'https://s.taobao.com/search?q={keyword}&page={page}')

    # 验证码拦截
    while browser.title == '验证码拦截':
        gui_text['text'] = f'出错：如有滑块验证请及时验证，程序将于验证后重新尝试爬取'
        gui_text['bg'] = 'red'
        gui_label_eta['text'] = '-'
        gui_label_now['text'] = f'-'
        time.sleep(2)

    # GUI显示
    gui_text['text'] = f'当前正在获取第{page}页，还有{page_end - page_start - page}页'
    gui_text['bg'] = '#10d269'

    # 定位元素
    try:
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
                month_deals = goods.find_element(By.CSS_SELECTOR,
                                                 'div.ctx-box.J_MouseEneterLeave.J_IconMoreNew > div.row.row-1.g-clearfix > div.deal-cnt').text.replace(
                    '人付款', '')
                ships_from = goods.find_element(By.CSS_SELECTOR,
                                                'div.ctx-box.J_MouseEneterLeave.J_IconMoreNew > div.row.row-3.g-clearfix > div.location').text
                shop_link = goods.find_element(By.CSS_SELECTOR,
                                               'div.ctx-box.J_MouseEneterLeave.J_IconMoreNew > div.row.row-3.g-clearfix > div.shop > a').get_attribute(
                    'href')
                item_link = goods.find_element(By.CSS_SELECTOR,
                                               'div.pic-box.J_MouseEneterLeave.J_PicBox > div > div.pic>a').get_attribute(
                    'href')
                goods_item = {"商品名称": item_name, "商品价格": item_price, "月销售量": month_deals,
                              "商品店铺名称": item_shop, "归属地": ships_from, "商品链接": item_link}
                output_list += [goods_item]

        elif tbPageVersion == 1:
            print('using new version selector')
            time.sleep(2)
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
                month_deals = goods.find_element(By.CSS_SELECTOR,
                                                 f'div:nth-child({i}) > a > div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > span.Price--realSales--FhTZc7U').text.replace(
                    '人付款', '').replace('人收货', '')
                ships_from_province = goods.find_element(By.CSS_SELECTOR,
                                                         f'div:nth-child({i}) > a > div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > div:nth-child(5) > span').text
                # 定位城市，由于有些没有城市属性所以需要try-except，但是很慢
                # try:
                #     ships_from_city = goods.find_element(By.CSS_SELECTOR,
                #                                          f'div:nth-child({i}) > a > div > div.Card--mainPicAndDesc--wvcDXaK > div.Price--priceWrapper--Q0Dn7pN > div:nth-child(6) > span').text
                # except:
                #     ships_from_city = ''
                ships_from_city = ''

                shop_link = goods.find_element(By.CSS_SELECTOR,
                                               f'div:nth-child({i})>a>div> div.ShopInfo--shopInfo--ORFs6rK  > div>a').get_attribute(
                    'href')
                item_link = goods.find_element(By.CSS_SELECTOR,
                                               f'div:nth-child({i})>a').get_attribute(
                    'href')
                goods_item = {"商品名称": item_name, "商品价格": item_price, "月销售量": month_deals,
                              "商品店铺名称": item_shop, "归属地": ships_from_province + ' ' + ships_from_city,
                              "商品链接": item_link}
                output_list += [goods_item]
    except:
        gui_text['text'] = f'本页面定位元素失败，程序将于5秒后重新尝试爬取'
        gui_text['bg'] = 'red'
        gui_label_eta['text'] = '暂无信息'
        gui_label_now['text'] = f'注意:第【{page}】页将跳过如需获取请重新运行程序！'
        print(f'注意:第【{page}】页将跳过如需获取请重新运行程序！')
        time.sleep(5)

    delay_time = random.randint(1, 5)
    for delay in range(delay_time):
        gui_label_now['text'] = '-'
        gui_text['bg'] = '#eeeeee'
        gui_text['text'] = f'第{page}页，还有{page_end - page_start - page}页'
        gui_label_eta['text'] = f'等待下次翻页{delay}秒，总共需等待{delay_time}秒'
        time.sleep(1)

gui_text['text'] = '正在导出xlsx'

output_dataframe = pandas.DataFrame(output_list)
output_dataframe.to_excel('淘宝爬取商品结果销售量排序' + f'{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}' + '.xlsx',
                          index=False)
gui_text['text'] = '保存文件完成，准备退出中'
time.sleep(5)
browser.close()
browser.quit()
sys.exit()
