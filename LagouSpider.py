import requests
from bs4 import BeautifulSoup
import math
import pandas as pd

keyword='数据分析'

#发送请求，获取html源码
def get_html(url):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Content-Encoding':'gzip',
        'Content-Language':'zh-CN',
        'Content-Type':'text/html;charset=UTF-8'
    }
    html = requests.get(url=url,headers=headers).text
    return html

#发送post请求，获取json数据
def post_html(url,parms,data):
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': '_ga=GA1.2.843009331.1522143717; user_trace_token=20180327174158-18250b07-31a3-11e8-b64b-5254005c3644; LGUID=20180327174158-18251096-31a3-11e8-b64b-5254005c3644; index_location_city=%E6%B7%B1%E5%9C%B3; WEBTJ-ID=20180420105641-162e0fb801a9-03260a2a52f61c-3e3d5f01-1440000-162e0fb801c159; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1522236861,1523868920,1523955273,1524193002; _gid=GA1.2.418725946.1524193002; JSESSIONID=ABAAABAAAFCAAEGCF5111EDC999DA1E0F13B661D440FB8E; TG-TRACK-CODE=search_code; X_HTTP_TOKEN=f8d8a15a08b06164afcf472f09183ffa; LGSID=20180420141612-530e8256-4462-11e8-b8bf-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html%3Fts%3D1524204971509%26serviceId%3Dlagou%26service%3Dhttps%25253A%25252F%25252Fwww.lagou.com%25252Fc%25252Fapprove.json%25253FcompanyIds%25253D119788%2525252C26399%2525252C128998%2525252C267%2525252C135243%2525252C5580%2525252C48687%2525252C7918%2525252C112144%2525252C79761%2525252C385%2525252C52004%2525252C28834%2525252C4558%2525252C16831%26action%3Dlogin%26signature%3D675394CC81B577C384B7623D9D76DE56; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1524205952; LGRID=20180420143232-9b6536a5-4464-11e8-b8c0-5254005c3644; SEARCH_ID=481e66da07ac4f8f8b745bc85c4ca57d',
        'Host': 'www.lagou.com',
        'Origin': 'https://www.lagou.com',
        'Referer': 'https://www.lagou.com/jobs/list_%E6%9C%BA%E5%99%A8%E5%AD%A6%E4%B9%A0?city=%E5%85%A8%E5%9B%BD&cl=false&fromSearch=true&labelWords=&suginput=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    }
    html = requests.post(url=url, headers=headers,data=data,params = parms).json()
    return html

#得到主要城市
def get_city(html):
    cityname=[]
    soup = BeautifulSoup(html,'lxml')
    cities = soup.select('.more-city-name')
    for city in cities:
        cityname.append(city.string)
    cityname = list(set(cityname))#进行去重
    return cityname

#每个城市有数据分析岗位需求的页码，将城市和页码信息进行保存到csv文件里面
def get_page(url,cities,pn=1):
    pages=[]
    for city in cities:
        params = {
            'city': city,
            'needAddtionalResult': 'false'
        }
        data = {
            'first': 'first',
            'pn': str(pn),
            'kd': keyword
        }
        jresult = post_html(url,parms=params,data=data)
        pagesize = jresult['content']['pageSize']
        total = jresult['content']['positionResult']['totalCount']
        page = math.ceil(total / float(pagesize))
        print(city, page)
        pages.append(page)
    cities_pages = {
        'city':cities,
        'page':pages
    }
    df = pd.DataFrame(cities_pages)
    df.to_csv('LagouCityPage.csv',encoding='gb18030',index=False)
    return cities_pages

#主体程序，
def main():
    city_url='https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90?px=default&city=%E5%85%A8%E5%9B%BD'
    html = get_html(city_url)
    cities=get_city(html)#得到主要的城市
    page_url = 'https://www.lagou.com/jobs/positionAjax.json'
    get_page(url=page_url,cities=cities)#根据主要的城市，获取每个城市的页码数，并进行保存到csv文件

if __name__=='__main__':
    main()