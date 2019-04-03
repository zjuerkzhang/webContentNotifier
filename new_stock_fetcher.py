#-*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
from general_fetcher import general_fetcher

g_link = "http://data.eastmoney.com/xg/xg/calendar.html"

class new_stock_fetcher(general_fetcher):
    def get_interested_content(self):
        ret_str = [] 
        soup = self.fetch_content_from_link()
        tds = soup.find_all("td", attrs={"class": "today", "valign":"top"})
        if len(tds) != 1:
            return  []
        else:
            divs = tds[0].find_all("div", attrs={"class": "cal_content"})
            if len(divs) != 1:
                return ["no divs with attribute 'class=cal_content'"]
            else:
                items = divs[0].find_all("div", attrs={"class": "cal_item"})
                for item in items:
                    bonds = item.find_all("b")
                    if len(bonds) != 1:
                        continue
                    else:
                        if bonds[0].string != u"申 购":
                            continue
                        else:
                            a_s = item.find_all("a")
                            for a in a_s:
                                stock_id = a["href"].replace("detail/", "").replace(".html", "")
                                temp_str = a.string + "(" + stock_id + ")"
                                ret_str.append(temp_str)
        return ret_str

if __name__ == "__main__":
    config = {}
    config['link'] = g_link
    stock_fetcher = new_stock_fetcher(config)
    new_stocks = stock_fetcher.get_interested_content()
    print("New stock today:")
    for stock in new_stocks:
        print(stock)
