import pandas as pd

import requests  

import re
import math
import random
import time
import sys, urllib


# 商品字段列表
products_columns = ['itemid', 'itemname', 'shopid', 'shopname', 'area', 'areaname', 
                    'author', 'press', 'price', 'binding', 'bindingname', 'pubdate', 'quality', 'qualityname', 
                    'bigimgurl', 'smallimgurl', 'biztype', 'catid', 'class', 'importantdesc', 'isrelatedisbn', 
                    'nickname', 'addtime', 'newaddtime', 'updatetime', 'years', 'years2', 'yearsgroup']

# 图书条目字段列表
items_columns = ['bookid', 'bookname', 'author', 'binding', 'bindingname', 'press',
                 'price', 'prodnum', 'newminprice', 'newprodnum', 'oldminprice', 'oldprodnum', 
                'pubdate', 'qualityname', 'bigimgurl', 'smallimgurl', 'subtitle', 'updatetime']

# 获取搜索结果函数
def search(key, unit='product', status=0, mode='isfuzzy', order=0, page=1, **kwargs):
    '''
        根据关键词搜索孔夫子旧书网所有商品
        @param key: search keywords, str
        @param unit: commodity units, str, default 'product'
        @param status: product status, int, default 0
        @param mode: search mode, str, default 'isfuzzy'
        @param order: sorting method, int, default 0
        @param page: page num, int, default=1
        @param kwargs: other conditions, Dict
        @return result: search results, Dict
    '''
    encode_key = urllib.parse.quote(key)
    
    # 搜索条件
    search_conditions = 'select=0&' + 'key=' + encode_key + '&status=' + str(status)
    for key, value in kwargs.items():
        value = value.encode('unicode_escape').decode()
        pattern = re.compile(r'\\u')
        encode_value  = re.sub(pattern, 'k', value)
        search_conditions += '&' + key
        if key=='author' or key=='press':
            search_conditions += '=h' + str(encode_value)
        else:
            search_conditions += '=' + str(encode_value)
    if unit=='product':
        search_conditions += '&' + mode + '=1' 
    search_conditions += '&order=' + str(order) 
    if page != 1:
        search_conditions += '&pagenum=' + str(page)
    
    #  Request URL 
    request_url = 'http://search.kongfz.com/' + unit + '_result/?' + search_conditions + '&type=1' + '&ajaxdata=1' + '&_=' + str(round(time.time() * 1000))
    
    # Request Headers
    my_headers = {
        'Host': 'search.kongfz.com',
        'Referer': 'http://search.kongfz.com/' + unit + '_result/?' + search_conditions,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    res = requests.post(url=request_url, headers = my_headers)  
    res.raise_for_status()  
    res.encoding = 'utf-8'  

    # 得到包含搜索结果的字典
    result = res.json()  
    return result

# 解析商品信息函数
def getPageInfo(unit, product_list, columns):  
    '''
        对一个网页的商品信息进行解析，返回结果列表
        @param unit: commodity units, str, default 'product'
        @param product_list: product list, List
        @param columns: columns list, List
        @return page_info_list: result list, List
    '''  
    page_info_list = []  
    
    for item in product_list:  
        product_info = []  
        for col in columns:
            try:
                product_info.append(item[col])
            except:
                product_info.append(None)
        if unit=='product':
            product_info.append('http://book.kongfz.com/' + item['shopid'] + '/' + item['itemid'] + '/')
        elif unit=='item':
            product_info.append('http://item.kongfz.com/book/' + item['bookid'] + '.html')
        page_info_list.append(product_info)  
    
    return page_info_list

# 爬取搜索结果列表数据函数
def kongfzSearchSpider(key, unit='product', status=0, mode='isfuzzy', order=0, page=1, **kwargs):  
    '''
        爬取孔夫子商品搜索结果列表数据，最多返回 5000 条搜索结果
        @param key: search keywords, str
        @param unit: commodity units, str, default 'product'
        @param status: product status, int, default 0;
        @param mode: search mode, str, default 'isfuzzy'
        @param order: sorting method, int, default 0
        @param page: page num, int, default=1
        @param kwargs: other conditions, Dict
    '''
    # 先爬取第一页，得到搜索结果的总记录数和总页数
    result_dict = search(key, unit, status, mode, order, page=1, **kwargs)
    total_found = result_dict['other']['total_found'] #获取总记录数
    page_num = result_dict['other']['page_count'] #获取总页数
    print('商品总数：{0}，总页数：{1}'.format(total_found, page_num))  
    time.sleep(30)
    
    if unit=='product':
        columns = products_columns
    elif unit=='item':
        columns = items_columns
    
    # 对每个网页读取JSON, 获取每页数据 
    total_info = [] 
    for n in range(1, page_num+1):  
        result_dict = search(key, unit, status, mode, order, page=n, **kwargs)  
        item_list = result_dict['data']['itemList']
        page_info = getPageInfo(unit, item_list, columns)
        total_info += page_info 
        print('第 {0}/{1} 页爬取完成'.format(n, page_num))
        time.sleep(random.randint(20, 40)) 
       
    #将所有数据转化为 DataFrame再输出 
    columns.append('detail_url')
    df = pd.DataFrame(data=total_info, columns=columns)   
    data_output = 'output\\' + key + '_' + str(round(time.time())) + '.csv'
    df.to_csv(data_output, index = False)
    print('爬虫结束')
    return df  
    


