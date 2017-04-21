# coding:utf-8
import datetime
import re
import csv
import requests
import time
from lxml import etree

from_date_lst = []
for year in range(2013,2018):
    for month in range(1,13):
        if month<10:
            date = str(year)+'-0'+str(month)+'-01'
        else:
            date = str(year)+'-'+str(month)+'-01'
        if date>str(datetime.datetime.now()):
            break
        from_date_lst.append(date)

def text_stamp(text_date):
    return int(time.mktime(time.strptime(text_date, "%Y-%m-%d")))

def gen_dates_lst():
    from_date_lst = []
    for year in range(2013, 2018):
        for month in range(1, 13):
            if month < 10:
                date = str(year) + '-0' + str(month) + '-01'
            else:
                date = str(year) + '-' + str(month) + '-01'
            if date > str(datetime.datetime.now()):
                break
            from_date_lst.append(date)

    to_date_lst = from_date_lst[1:]
    to_date_lst.append(str(datetime.datetime.now())[:10])

    return zip(from_date_lst,to_date_lst)


def get_pages(keywords,date_range):
    start,end = text_stamp(date_range[0]),text_stamp(date_range[1])
    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch, br',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'www.baidu.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
    }

    params = {
        'wd':'%s'%keywords,
        'rsv_spt':'1',
        'rsv_iqid':'0xda46c513000055cf',
        'issp':'1',
        'f':'3',
        'rsv_bp':'1',
        'rsv_idx':'2',
        'ie':'utf-8',
        'rqlang':'cn',
        'tn':'baiduhome_pg',
        'rsv_enter':'1',
        'rsv_t':'0812O7i+y0JjSPVRTrdimxurfW/QPpRYr3Ldy1jKS5PMfPUB3NSZGEPWTbpjscBa9HES',
        'inputT':'1603',
        'gpc':'stf=%d,%d|stftype=2'%(start,end),
        'tfflag':'1'
    }
    res = requests.get('https://www.baidu.com/s', headers=headers, params=params)

    return res

def extract_report_nums(res):
    selector = etree.HTML(res.text)
    content = selector.xpath('//*[@id="container"]/div[2]/div/div[2]/text()')[0]
    report_nums = re.search('\d+',content)

    return report_nums.group()

if __name__ == '__main__':
    keywords = '杨浦 创业'
    with open('杨浦+创业 按月获取网页报道数量 2017-04-21.csv','w',encoding='gbk',newline='') as file:
        writer = csv.writer(file)
        writer.writerow(('ID','关键词','开始时间','结束时间','网页报道量','对应地址'))
        date_range_zip = gen_dates_lst()

        for id,date_range in enumerate(date_range_zip):
            try:
                res = get_pages(keywords,date_range)
            except Exception as e:
                print(e)
            else:
                report_nums = extract_report_nums(res)
                writer.writerow((id+1,keywords,date_range[0],date_range[1],report_nums,res.url))
                print(id+1,keywords,date_range[0],date_range[1],report_nums,res.url)
            finally:
                time.sleep(2)
