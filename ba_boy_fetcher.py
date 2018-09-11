#-*- coding: UTF-8 -*-
from general_fetcher import general_fetcher
import urllib2
import json
import time
import codecs
import os

g_link = "http://www.ba.de/searchapi/v1/search?kw=pari&boy"
g_price_dir = "/root/uni_notify/history_price/"
g_price_file = g_price_dir + "ba_price.txt"

class ba_boy_fetcher(general_fetcher):
    def write_to_file(self, p_file, p_str):
        log_file = codecs.open(p_file, 'a+','utf-8')
        log_file.write(p_str+'\n')
        log_file.close()

    def get_last_price_by_name(self, name):
        name = name.encode("utf-8")
        if not os.path.exists(g_price_file):
            return '0.0'
        with open(g_price_file, 'r') as myfile:
            data = myfile.read()
            lines = data.split('\n')[:-1]
            kw_lines = filter(lambda x:x.find(name)>=0, lines)
            if len(kw_lines) <= 0:
                return "0.0"
            ret_val = kw_lines[-1].split(" ")[-1]
        return ret_val

    def get_interested_content(self):
        page = urllib2.urlopen(self.config['link'])
        if not page:
            return [("[Error]: no content is fetched from link [%S]" % self.config['link'])]
        try:
            json_data = json.load(page)
        except:
            return ["[Error]: Fail to parse the JSON content"]
        ret_strs = []
        item_list = json_data['data']
        for item in item_list:
            if item['name'] in self.config['keywords']:
                #print "hit %s" % item['name']
                last_price = self.get_last_price_by_name(item['name'])
                if float(last_price) != float(item['final_price']):
                    ret_strs.append("%s [%s] %s => %s" % (time.strftime("%Y-%m-%d"), item['name'], last_price, item['final_price'] ))
        if len(ret_strs) > 0:
            for one_str in ret_strs:
                self.write_to_file(g_price_file, one_str)
        return ret_strs

if __name__ == "__main__":
    config = {}
    config['link'] = g_link
    config['keywords'] = []
    config['keywords'].append(u"PARI 百瑞 JUNIOR BOY SX 婴儿儿童雾化器 0-12岁儿童专用")
    config['keywords'].append(u"PARI 百瑞 BOY SX 雾化器 4+")
    fetcher = ba_boy_fetcher(config)
    price_info = fetcher.get_interested_content()
    print "price change today:"
    for price in price_info:
        print price
