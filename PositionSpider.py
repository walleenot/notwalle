import pandas as pd
from LagouSpider import post_html,keyword
import pymongo
from json.decoder import JSONDecodeError

#MongoDB的配置
MONGO_URL = 'localhost'
MONGO_DB = 'LaGou'#名称
MONGO_TABLE = 'DataA'
#配置MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

#保存到MongoDB
def save_to_mongo(info):
    try:
        if db[MONGO_TABLE].insert(info):
            print('成功保存到数据库',info)
    except Exception:
        print('保存失败！',info)

#得到每个职位的相关信息，并保存到MongoDB
def get_position_info(page,city,url):
    params = {
        'city': city,
        'needAddtionalResult': 'false'
    }
    for pn in range(1,page+1):
        data = {
            'first': 'first',
            'pn': str(pn),
            'kd': keyword
        }
        try:
            jresult = post_html(url=url,parms=params,data=data)
            results = jresult['content']['positionResult']['result']
            for i in range(len(results)):
                info={
                    'businessZones':results[i]['businessZones'],
                    'city':results[i]['city'],
                    'companyFullName':results[i]['companyFullName'],
                    'companyShortName':results[i]['companyShortName'],
                    'companySize':results[i]['companySize'],
                    'createTime':results[i]['createTime'],
                    'district':results[i]['district'],
                    'education':results[i]['education'],
                    'industryField':results[i]['industryField'],
                    'industryLables':results[i]['industryLables'],
                    'jobNature':results[i]['jobNature'],
                    'positionId':results[i]['positionId'],
                    'workYear':results[i]['workYear'],
                    'salary':results[i]['salary']
                }
                save_to_mongo(info)
        except JSONDecodeError:
            continue

#主体程序
def main():
    df = pd.read_csv('LagouCityPage.csv',encoding='gb18030')
    df = df[df['page']>0]#过滤，将页码为0的城市剔除
    url='https://www.lagou.com/jobs/positionAjax.json'
    cities = list(df['city'])
    pages = list(df['page'])
    #根据城市和页码数，进行请求，获取主要职位信息
    for i in range(len(cities)):
        city = cities[i]
        page = pages[i]
        get_position_info(page,city,url)

if __name__=='__main__':
    main()

