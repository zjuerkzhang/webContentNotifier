import os
from xml.dom.minidom import parse

sample_config_file = "config.xml"

def get_keyword_from_xml(config_file = sample_config_file):
    config = []
    if os.path.isfile(config_file):
        xml_dom = parse(config_file)
        root = xml_dom.documentElement
        items = root.getElementsByTagName("section")
        for item in items:
            entry = {}
            name = item.getElementsByTagName("name")
            entry['name'] = name[0].childNodes[0].data
            nick = item.getElementsByTagName('fetcher')
            entry['fetcher'] = nick[0].childNodes[0].data
            nick = item.getElementsByTagName('link')
            entry['link'] = nick[0].childNodes[0].data
            nick = item.getElementsByTagName('schedule')
            entry['schedule'] = nick[0].childNodes[0].data
            nick = item.getElementsByTagName('keywords')
            if not nick:
                entry['keywords'] =[] 
            else:
                kws_str = nick[0].childNodes[0].data
                entry['keywords'] = kws_str.split('|')
            config.append(entry)
        return config
    else:
        return config

if __name__ == '__main__':
    config = get_keyword_from_xml(sample_config_file)
    for entry in config:
        print(entry['name'])
        print(" "*3 + entry['fetcher'])
        print(" "*3 + entry['link'])
        print(" "*3 + entry['schedule'])
        print(" "*3 + "keywords:")
        for kw in entry['keywords']:
            print(" "*6 + kw)
