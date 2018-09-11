#-*- coding: UTF-8 -*-
import csv
import urllib2
import os
import time
from bs4 import BeautifulSoup
import threading
import sys

g_house_csv_file = "link_home_house.csv"
g_linkhome_url_temp = "http://hz.lianjia.com/ershoufang/pg%dco32/"
g_linkhome_house_temp = "http://hz.lianjia.com/ershoufang/"
g_house_infos = []
lock = threading.Lock()

def fetch_content_from_link(link):
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(link, headers=hdr)
    try:
        page = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print e.code
        print e.read()
        return None
    try:
        soup = BeautifulSoup(page, 'html5lib')
    except httplib.IncompleteRead:
        soup = None
    #print soup.prettify()
    return soup

def get_old_house_ids():
    if not os.path.exists(g_house_csv_file):
        return []
    ids = []
    with open(g_house_csv_file, "rb") as f:
        rows = csv.reader(f)
        headers = next(rows)
        for row in rows:
            ids.append(row[0])
    return ids

def generate_page_link(page_num):
    return (g_linkhome_url_temp % page_num)

def get_house_ids_from_page(link):
    ids = []
    soup = fetch_content_from_link(link)
    if not soup:
        return ids
    else:
        house_entries = soup.find_all("div", attrs={"class": "info clear"})
        for entry in house_entries:
            priceInfos = entry.find_all("div", attrs={"class": "priceInfo"})
            if len(priceInfos) != 1:
                continue
            else:
                unitPrices = priceInfos[0].find_all("div", attrs={"class": "unitPrice"})
                if len(unitPrices) != 1:
                    continue
                else:
                    ids.append(unitPrices[0]["data-hid"])
    if len(ids) <= 0:
        pass
        #print soup.prettify()
    return ids

def filter_old_ids(ids, old_ids):
    ret_ids = []
    for new_id in ids:
        exist_in_old = False
        for old_id in old_ids:
            if old_id == new_id.encode("ascii"):
                exist_in_old = True
                break
        if not exist_in_old:
            ret_ids.append(new_id)
    return ret_ids

def get_community(soup):
    communities = soup.find_all("div", attrs={"class": "communityName"})
    if len(communities) != 1:
        return ""
    a_s = communities[0].find_all("a", attrs={"class": "info"})
    if len(a_s) != 1:
        return ""
    return a_s[0].string

def get_wheres(soup):
    wheres = []
    divs = soup.find_all("div", attrs={"class": "areaName"})
    if len(divs) != 1:
        return wheres
    a_s = divs[0].find_all("a", attrs={"target": "_blank"})
    for a in a_s:
        wheres.append(a.string)
    return wheres

def get_room_cnts(soup):
    room_cnts ={} 
    base_infos = soup.find_all("div", attrs={"class": "base"})
    if len(base_infos) != 1:
        return room_cnts
    lis = base_infos[0].find_all("li")
    for li in lis:
        spans = li.find_all("span")
        if len(spans) != 1:
            continue
        if spans[0].string == u"房屋户型":
            room_str = li.contents[1]
            temp_strs = room_str.split(u"室")
            room_cnts["bedroom"] = temp_strs[0]
            temp_strs = temp_strs[1].split(u"厅")
            room_cnts["hall"] = temp_strs[0]
            temp_strs = temp_strs[1].split(u"厨")
            room_cnts["kidroom"] = temp_strs[0]
            temp_strs = temp_strs[1].split(u"卫")
            room_cnts["wc"] = temp_strs[0]
            return room_cnts
    return room_cnts
    
def get_floor_info(soup):
    floor_info = {} 
    rooms = soup.find_all("div", attrs={"class": "room"})
    if len(rooms) != 1:
        return floor_info 
    divs = rooms[0].find_all("div", attrs={"class": "subInfo"})
    if len(divs) != 1:
        return ""
    floor_strs = divs[0].string.split("/")
    floor_info["total_floor"] = floor_strs[1].replace(u"共", "").replace(u"层", "")
    floor_info["current_floor"] = floor_strs[0].replace(u"楼层", "")
    return floor_info
    

def get_area(soup):
    areas = soup.find_all("div", attrs={"class": "area"})
    if len(areas) != 1:
        return ""
    divs = areas[0].find_all("div", attrs={"class": "mainInfo"})
    if len(divs) != 1:
        return ""
    return divs[0].string.replace(u"平米", "")

def get_total_price(soup):
    prices = soup.find_all("div", attrs={"class": "price "})
    if len(prices) != 1:
        return ""
    totals = prices[0].find_all("span", attrs={"class": "total"})
    if len(totals) != 1:
        return ""
    return totals[0].string

def get_unit_price(soup):
    units = soup.find_all("span", attrs={"class": "unitPriceValue"})
    if len(units) != 1:
        return ""
    return units[0].contents[0]

def get_pub_date(soup):
    trans = soup.find_all("div", attrs={"class": "transaction"})
    if len(trans) != 1:
        return ""
    lis = trans[0].find_all("li")
    for li in lis:
        spans = li.find_all("span")
        if len(spans) != 1:
            continue
        if spans[0].string == u"挂牌时间":
            return li.contents[1]
    return ""

def get_direct(soup):
    types = soup.find_all("div", attrs={"class": "type"})
    if len(types) != 1:
        return ""
    divs = types[0].find_all("div", attrs={"class": "mainInfo"})
    if len(divs) != 1:
        return ""
    return divs[0].string

def get_house_info_by_id(house_id):
    global g_house_infos
    info = {}
    link = g_linkhome_house_temp + house_id + ".html"
    soup = fetch_content_from_link(link)
    if not soup:
        return info
    else:
        info = {"id": house_id}
        info["community"] = get_community(soup)
        wheres = get_wheres(soup)
        if len(wheres) == 1:
            info["where0"] = wheres[0]
            info["where1"] = ""
        elif len(wheres) >= 2:
            info["where0"] = wheres[0]
            info["where1"] = wheres[1]
        else:
            info["where0"] = ""
            info["where1"] = ""
        room_cnts = get_room_cnts(soup)
        if len(room_cnts) > 0:
            info["bedroom_cnt"] = room_cnts["bedroom"]
            info["hall_cnt"] = room_cnts["hall"]
            info["wc_cnt"] = room_cnts["wc"]
        else:
            info["bedroom_cnt"] = ""
            info["hall_cnt"] = ""
            info["wc_cnt"] = ""
        floor_info = get_floor_info(soup)
        if len(floor_info) > 0:
            info["total_floor"] = floor_info["total_floor"]
            info["current_floor"] = floor_info["current_floor"]
        else:
            info["total_floor"] = ""
            info["current_floor"] = ""
        info["area"] = get_area(soup)
        info["total_price"] = get_total_price(soup)
        info["unit_price"] = get_unit_price(soup)
        info["pub_date"] = get_pub_date(soup)
        info["direct"] = get_direct(soup)
    if info["community"] == "":
        return {}
    #print info["id"], info["community"], info["where0"], info["where1"], info["total_floor"], info["current_floor"], info["total_price"], info["area"], info["unit_price"], info["pub_date"]
    return info

def transfer_dict_to_list(dict_item):
    list_item = []
    list_item.append(dict_item["id"])
    list_item.append(dict_item["pub_date"])
    list_item.append(dict_item["community"])
    list_item.append(dict_item["area"])
    list_item.append(dict_item["total_price"])
    list_item.append(dict_item["unit_price"])
    list_item.append(dict_item["total_floor"])
    list_item.append(dict_item["current_floor"])
    list_item.append(dict_item["bedroom_cnt"])
    list_item.append(dict_item["hall_cnt"])
    list_item.append(dict_item["wc_cnt"])
    list_item.append(dict_item["where0"])
    list_item.append(dict_item["where1"])
    list_item.append(dict_item["direct"])
    return list_item

def write_to_csv_file(house_infos):
    head_need = False
    if not os.path.exists(g_house_csv_file):
        head_need = True
    headers = ["id", "pub_date", "community", "area", "total_price", "unit_price", "total_floor", "current_floor", "bedroom_cnt", "hall_cnt", "wc_cnt", "where0", "where1", "direct"]
    with open(g_house_csv_file, "a+") as f:
        rows = csv.writer(f)
        if head_need:
            f.write(u'\ufeff'.encode('utf8'))
            rows.writerow(headers)
        for info in house_infos:
            list_info = transfer_dict_to_list(info)
            rows.writerow([item.encode('utf8') for item in list_info]) 

def fetch_house_info():
    global g_house_infos
    old_ids = get_old_house_ids()
    last_page = False
    new_added = False
    for page_num in range(1,101):
        print("page %d" % page_num)
        house_infos = []
        thread_table = []
        link = generate_page_link(page_num)
        page_ids = get_house_ids_from_page(link)
        time.sleep(30)
        new_ids = filter_old_ids(page_ids, old_ids)
        if len(page_ids)<=0: #len(new_ids)<len(page_ids) or len(page_ids)<=0:
            last_page = True
        for house_id in new_ids:
            print("house index %d" % new_ids.index(house_id))
            house_info = get_house_info_by_id(house_id)
            if len(house_info) > 0:
                house_infos.append(house_info)
            time.sleep(10)
            #thread_entry = threading.Thread(target=get_house_info_by_id, args=(house_id,))
            #thread_entry.start()
            #thread_table.append(thread_entry)
        #for thrd in thread_table:
            #thrd.join()
        if len(house_infos) > 0:
            write_to_csv_file(house_infos) 
            new_added = True
        if last_page:
            break
    return new_added

if __name__ == "__main__":
    house_id = "103101275340"
    house_info = get_house_info_by_id(house_id)
    print house_info
    print house_info['id']
    print house_info['pub_date']
    print house_info['communitry']
