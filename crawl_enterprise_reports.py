# -*- coding:utf-8-*-
import csv
import datetime
import re

import requests
import time
from lxml import etree

class NetReportsCrawler(object):
    """网页报道量抓取"""
    def __init__(self,keywords):
        self.keywords = keywords

    def _text_stamp(self,text_date):
        """将xxxx-xx-xx文本型日期转换为时间戳"""
        return int(time.mktime(time.strptime(text_date, "%Y-%m-%d")))

    def get_response(self,keywords, date_range):
        """获取response"""
        start = self._text_stamp(date_range[0])
        end = self._text_stamp(date_range[1])
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.baidu.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
        }

        params = {
            'wd': '%s' % keywords,
            'rsv_spt': '1',
            'rsv_iqid': '0xda46c513000055cf',
            'issp': '1',
            'f': '3',
            'rsv_bp': '1',
            'rsv_idx': '2',
            'ie': 'utf-8',
            'rqlang': 'cn',
            'tn': 'baiduhome_pg',
            'rsv_enter': '1',
            'rsv_t': '0812O7i+y0JjSPVRTrdimxurfW/QPpRYr3Ldy1jKS5PMfPUB3NSZGEPWTbpjscBa9HES',
            'inputT': '1603',
            'gpc': 'stf=%d,%d|stftype=2' % (start, end),
            'tfflag': '1'
        }
        res = requests.get('https://www.baidu.com/s', headers=headers, params=params)

        return res

    def extract_report_nums(self,res):
        """抽取报道数量"""
        selector = etree.HTML(res.text)
        content = selector.xpath('//*[@id="container"]/div[2]/div/div[2]/text()')[0]
        report_nums = re.findall('约(.*?)个', content)
        return report_nums[0]

    def do_crawl(self,keywords,start_lst,end_lst,csv_filename,sampleid):
        """执行爬虫并写入csv文件"""
        csvfile = open(csv_filename, 'a', encoding='gbk', newline='')
        csvwriter = csv.writer(csvfile)

        for monthid,date_range in enumerate(zip(start_lst,end_lst)):
            try:
                res = self.get_response(keywords,date_range)
            except Exception as e:
                print(e)
            else:
                report_nums = self.extract_report_nums(res)
                write_info = (
                    sampleid+1,
                    monthid+1,
                    keywords,
                    date_range[0],
                    date_range[1],
                    report_nums,res.url
                )
                csvwriter.writerow(write_info)
                print(sampleid+1,monthid+1,keywords,report_nums)
        csvfile.close()

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

    return from_date_lst, to_date_lst

if __name__ == '__main__':

    csv_filename = '各个公司 按月网页报道数量 2017-04-22.csv'
    from_date_lst, to_date_lst = gen_dates_lst()

    with open('companylist.txt',encoding='utf-8',mode='r') as keywords_file:
        keywords_lst = keywords_file.read().split('\n')

    csvfile = open(csv_filename,'a',encoding='gbk',newline='')
    csvwriter = csv.writer(csvfile)
    title = ('SampleID','MonthID','关键词','开始时间','结束时间','网页报道量','对应地址')
    csvwriter.writerow(title)
    csvfile.close()

    for sampleid,keywords in enumerate(keywords_lst):
        if sampleid >= 0:
            try:
                nrc = NetReportsCrawler(keywords)
                nrc.do_crawl(keywords,from_date_lst,to_date_lst,csv_filename,sampleid)
            except:
                print(sampleid+1)