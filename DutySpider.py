import requests
import pymongo
import pandas as pd
from bs4 import BeautifulSoup

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
        if db['Description'].insert(info):
            print('成功保存到数据库',info)
    except Exception:
        print('保存失败！',info)

#发送请求，获取每个职位的职位描述和职位职责
def get_discribe(s):
    url='https://www.lagou.com/jobs/'+str(s)+'.html'
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
    try:
        response=requests.get(url=url, headers=headers)
        print(response.url)
        html = response.text
        soup = BeautifulSoup(html,'lxml')
        description = soup.select('.job_bt')[0].get_text().strip()
        describe = {
            'description':description,
            'positionId':str(s)
        }
        save_to_mongo(describe)
        return description
    except IndexError:
        print('重新请求')
        return get_discribe(s)

#从MongoDB获取职位的相关信息，并根据positionId发送请求，获取职位描述，保存到csv文件
def get_info_from_mongo():
    businessZoneses=[]
    cities=[]
    companyFullNames=[]
    companyShortNames=[]
    companySizes=[]
    createTimes=[]
    districts=[]
    educations=[]
    industryFields=[]
    industryLableses=[]
    jobNatures=[]
    positionIds=[]
    workYears=[]
    salarys=[]
    res=db[MONGO_TABLE].find()
    for r in res:
        businessZoneses.append(r['businessZones'])
        cities.append(r['city'])
        companyFullNames.append(r['companyFullName'])
        companyShortNames.append(r['companyShortName'])
        companySizes.append(r['companySize'])
        createTimes.append(r['createTime'])
        districts.append(r['district'])
        educations.append(r['education'])
        industryFields.append(r['industryField'])
        industryLableses.append(r['industryLables'])
        jobNatures.append(r['jobNature'])
        positionIds.append(r['positionId'])
        workYears.append(r['workYear'])
        salarys.append(r['salary'])
    info = {
        'businessZones': businessZoneses,
        'city': cities,
        'companyFullName':companyFullNames,
        'companyShortName': companyShortNames,
        'companySize':companySizes,
        'createTime': createTimes,
        'district':districts,
        'education':educations,
        'industryField': industryFields,
        'industryLables': industryLableses,
        'jobNature': jobNatures,
        'positionId': positionIds,
        'workYear':workYears,
        'salary': salarys
    }
    df=pd.DataFrame(info)
    df = df[~(df['positionId'].duplicated())]#根据positionId进行去重
    #print(df['positionId'].duplicated().value_counts())
    df['description'] = df['positionId'].apply(get_discribe)#根据positionId发送请求，获取职位描述信息
    df.to_csv('LagouPosition1234.csv',encoding='gb18030',index=False)#保存到csv文件

#主体程序
def main():
    get_info_from_mongo()

if __name__=='__main__':
    main()