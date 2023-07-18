import time

import requests
from bs4 import BeautifulSoup
import pandas

f = open('./settings.ini', 'r+', encoding='utf8')
CONST_KEY_WORD = str(f.readline().strip())
CONST_BEGIN_PAGE = int(f.readline().strip())
CONST_END_PAGE = int(f.readline().strip())
f.close()
# CONST_KEY_WORD = str(input("请输入搜索的商品名称"))
# CONST_BEGIN_PAGE = int(input("请输入起始搜索页面页码"))
# CONST_END_PAGE = int(input("请输入终止搜索页面页码"))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
}

output_list = []
for index in range(CONST_BEGIN_PAGE, CONST_END_PAGE):
    jd_url = "https://search.jd.com/Search?keyword=" + CONST_KEY_WORD + "&page=" + str(index)
    jd_response = requests.get(jd_url, headers=headers)
    jd_soup = BeautifulSoup(jd_response.text, "html.parser")
    jd_items = jd_soup.select(".gl-item")
    for item in jd_items:
        title = item.select(".p-name em")[0].get_text().strip()
        item_link = item.select(".p-name a")[0].get("href")
        price = item.select(".p-price i")[0].get_text().strip()
        shop = item.select(".p-shop span")[0].get_text().strip()
        shop_link = item.select(".p-shop span a")[0].get("href")
        icons = item.select(".p-icons")
        icon_list = []
        for icon in icons:
            icon_list += icon.get_text().strip().split('\n')
        goods_item = {'商品标题': title, '商品价格': price, '商品链接': '''https:''' + item_link, '商家名称': shop,
                      '商家链接': '''https:''' + shop_link,
                      '产品标识': icon_list}
        output_list += [goods_item]
        print(goods_item)
    time.sleep(1)

output_dataframe = pandas.DataFrame(output_list)
output_dataframe.to_excel('京东爬取商品结果' + f'{time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())}' + '.xlsx',
                          index=False)