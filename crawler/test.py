#-*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import requests

host = 'https://www.ptt.cc'
url = 'https://www.ptt.cc/bbs/Food/index1.html'

res = requests.get(url)
soup = BeautifulSoup(res.text, 'lxml')

print(soup.find_all('a',class_='btn wide', text='下頁 ›')[0].get('href'))

exit(0)

def get_menu_page_info(menu_page_url):
    res = requests.get(menu_page_url)
    soup = BeautifulSoup(res.text, 'lxml')

    menu_page_data = []
    for entry in soup.select('.r-ent'):
        data = {
            'title': entry.select('.title')[0].text,
            'post_url': host + entry.select('.title > a')[0].get('href') if entry.select('.title > a') else None,
            'date': entry.select('.date')[0].text,
            'author': entry.select('.author')[0].text
        }
        menu_page_data.append(data)

    return menu_page_data

def get_post_detail_info(post_url):
    res = requests.get(post_url)
    soup = BeautifulSoup(res.text, 'lxml')

    # 標題部分，抓 author, title, date_time
    metalines = soup.select('.article-metaline')
    author, title, date_time = None, None, None
    for metaline in metalines:
        if metaline.select('.article-meta-tag') and metaline.select('.article-meta-tag')[0].text == '作者':
            author = metaline.select('.article-meta-value')[0].text if metaline.select('.article-meta-value') else None
        elif metaline.select('.article-meta-tag') and metaline.select('.article-meta-tag')[0].text == '標題':
            title = metaline.select('.article-meta-value')[0].text if metaline.select('.article-meta-value') else None
        elif metaline.select('.article-meta-tag') and metaline.select('.article-meta-tag')[0].text == '時間':
            post_date_time = metaline.select('.article-meta-value')[0].text if metaline.select('.article-meta-value') else None

    # 其他 infos
    others_infos = []
    others = soup.select('span.f2')
    for other in others:
        others_info.append(other.text)

    # 過濾已爬 tags 資訊
    ignore_tags = ['.article-metaline']
    for tag in soup.find_all(class_=['article-metaline','article-metaline-right','f2']):
        tag.replace_with('')

    # 主文
    body_content = soup.select('#main-content')[0].text.strip()

    # 推文資訊
    push_infos = []
    pushes = soup.select('.push')
    for push in pushes:
        push_tag = push.select('.push-tag')[0].text if push.select('.push-tag') else None
        push_author = push.select('.push-userid')[0].text if push.select('.push-userid') else None
        push_content = push.select('.push-content')[0].text if push.select('.push-content') else None
        push_date_time = push.select('.push-ipdatetime')[0].text if push.select('.push-ipdatetime') else push.select('.push-ipdatetime')
        data = {
            'push_tag': push_tag,
            'push_author': push_author,
            'push_content': push_content,
            'push_date_time': push_date_time

        }
        push_infos.append(data)




my_post_url = 'https://www.ptt.cc/bbs/sex/M.1467099969.A.1D1.html'
get_post_detail_info('https://www.ptt.cc/bbs/Food/M.1468240269.A.009.html')


# doc = {
#     'body_content': body_content,
#     'push_infos',
#     'other_infos',
#     'author',
#     'title',
#     'post_date_time'
# }