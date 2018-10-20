import time
import random
import requests

import re
from bs4 import BeautifulSoup


def getSoup(url, refer_url):
    """

    """
    my_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
        'Host': 'search.51job.com',
        'Refer': refer_url
    }

    res = requests.get(url, headers = my_headers)
    res.raise_for_status() 
    res.encoding = 'GBK'

    soup = BeautifulSoup(res.text, 'html.parser')

    return soup


def parsePosDetail(soup):
    """
        
    """
    soup = soup

    pos_info = []

    pos_info.append(soup.find('div', 'tHjob').h1.input['value'])                     #职位id
    pos_info.append(soup.find('div', 'tHjob').h1['title'])                           #职位名称
    pos_info.append(soup.find('p', 'cname').a['href'].split('co')[-1].split('.')[0]) #公司id
    pos_info.append(soup.find('p', 'cname').a['title'])                              #公司名称
    pos_info.append(soup.find('p', 'cname').a['href'])                               #公司主页url

    # 职位标签
    label_list = soup.find('div', 'jtag').find_all('span', 'sp4')
    pos_label = ""
    for label in label_list:
        pos_label += label.get_text() + ","
    pos_info.append(pos_label)

    # 薪资范围
    if soup.find('div', 'tHjob').strong.get_text() == "":
        min_salary = 0
        max_salary = 0

    salary = soup.find('div', 'tHjob').strong.get_text().split('/')
    salary_unit = salary[0][-1]
    salary_time = salary[1]
    min_salary = float(salary[0].split('-')[0])
    max_salary = float(salary[0].split('-')[1][:-1])

    if salary_time == "年":
        min_salary /= 12
        max_salary /= 12
    elif salary_time == "天":
        min_salary = 0
        max_salary = 0
    
    if salary_unit == "千":
        min_salary *= 1000
        max_salary *= 1000
    elif salary_unit == "万":
        min_salary *= 10000
        max_salary *= 10000
    
    pos_info.append(min_salary) #最低薪资
    pos_info.append(max_salary) #最高薪资

    # 其他信息
    other_msg = re.split(r'\xa0\xa0|\xa0\xa0', soup.find('p', 'ltype')['title'])
    while '|' in other_msg:
        other_msg.remove('|')
    
    pos_info.append(other_msg[0].split('-')[0] + '市') #城市
    try:
        pos_info.append(other_msg[0].split('-')[0] + '市' + other_msg[0].split('-')[1]) #城市加区（县）
    except:
        pos_info.append(other_msg[0].split('-')[0] + '市') 
    pos_info.append(other_msg[1])     #工作年限
    if len(other_msg)>=5:
        pos_info.append(other_msg[2]) #最低学历
        pos_info.append(other_msg[3]) #招聘人数
        pos_info.append(other_msg[4]) #发布时间
    else:
        pos_info.append("")           #最低学历
        pos_info.append(other_msg[2]) #招聘人数
        pos_info.append(other_msg[3]) #发布时间

    # 职位类别和职位关键字
    pos_fp = soup.find('div', 'tCompany_main').find('div', 'job_msg').find('div', 'mt10').extract().find_all('p', 'fp')

    cate_list = pos_fp[0].find_all('span', 'el')
        pos_cate = ""
    for i in cate_list:
        pos_cate += i.get_text() + ","
    pos_info.append(pos_cate)

    try:
        key_list = pos_fp[1].find_all('span', 'el')
        pos_key = ""
        for i in key_list:
            pos_key += i.get_text() + ","
        pos_info.append(pos_key)
    except:
        pos_info.append("")

    # 职位描述
    share = soup.find('div', 'tCompany_main').find('div', 'job_msg').find('div', 'share').extract() #微信分享
    tmp = soup.find('div', 'tCompany_main').find('div', 'job_msg').prettify()
    pattern = re.compile("<(.|\n)+?>\\n\s*")
    pos_desc = re.sub(pattern, "", tmp)
    pos_info.append(pos_desc)

    return pos_info


def getPosDetail(url, refer_url):
    """
    
    """
    pos_detail = parsePosDetail(getSoup(url, refer_url))
    return pos_detail
