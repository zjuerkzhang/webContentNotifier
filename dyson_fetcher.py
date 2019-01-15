#-*- coding: UTF-8 -*-
from general_fetcher import general_fetcher
import urllib2
import json
import time
import codecs
import os

g_link = "http://shop.dyson.cn/vacuums/cordless-vacuums/"
g_price_dir = "/root/webContentNotifier/history_price/"
g_price_file = g_price_dir + "dyson_price.txt"

class dyson_fetcher(general_fetcher):
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

    def entry_in_wanted_list(self, entry, wanted_list):
        for wanted_str in wanted_list:
            if entry.find(wanted_str) >= 0:
                return wanted_str
        return ''

    def get_interested_content(self):
        soup = self.fetch_content_from_link()
        if not soup:
            return [("[Error]: no content is fetched from link [%S]" % self.config['link'])]
        divs = soup.find_all("div", {'class': 'col-md-5 col-md-push-7 col-xs-6 category-item-description'})
        if len(divs) <= 0:
            return [("[Error]: no <div> is fetched from link [%S]" % self.config['link'])]
        now_price = []
        for div in divs:
            product = {'name':'', 'price': ''}
            a = div.find("a")
            if not a:
                return [("[Error]: no <a> is fetched from <div> [%S]" % div.prettify())]
            if not a.string:
                return [("[Error]: no string is fetched from <a> [%S]" % a.prettify())]
            hit_kw = self.entry_in_wanted_list(a.string, self.config['keywords'])
            if len(hit_kw) > 0:
                #print "hit %s" % hit_kw
                product['name'] = hit_kw
                price_span = div.find('span', {'class':'price'})
                if not price_span:
                    return [("[Error]: no price <span> is fetched from <div> [%S]" % div.prettify())]
                if not price_span.string:
                    return [("[Error]: no string is fetched from <span> [%S]" % price_span.prettify())]
                price_str = price_span.string
                product['final_price'] = price_str.split('.')[0].replace(',', '').replace(u'￥','')
                now_price.append(product)
        #print now_price
        ret_strs = []
        for item in now_price:
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
    config['keywords'].append("Dyson V8 Fluffy")
    config['keywords'].append("Dyson V7 Fluffy")
    config['keywords'].append("Dyson V6 Fluffy Extra")
    fetcher = dyson_fetcher(config)
    price_info = fetcher.get_interested_content()
    print "price change today:"
    for price in price_info:
        print price
