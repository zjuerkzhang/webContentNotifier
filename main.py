#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time
import sys
import os
import get_config
import send_163_mail
import message_pusher
from general_fetcher import general_fetcher
from new_stock_fetcher import new_stock_fetcher

g_message = ""
lock = threading.Lock()

def run_thread(config):
    global g_message
    fetcher_inst_cmd = config["fetcher"] + "(config)"
    fetcher = eval(fetcher_inst_cmd)
    ret_strs = fetcher.get_interested_content()
    if len(ret_strs) > 0:
        temp_str = "="*20 + "\n"
        temp_str += ("Content from %s\n" % config["name"])
        for str_entry in ret_strs:
            temp_str += (" "*4 + str_entry + "\n")
        temp_str += "\n"
        lock.acquire()
        g_message += temp_str
        lock.release()
    else:
        print("No content from %s" % config["name"])
        
def need_thread_created_for_job(schedule_str):
    now_time = time.localtime(time.time())
    now_time_value = now_time.tm_hour * 60 + now_time.tm_min
    [h, m] = schedule_str.split(".")
    if h.find("*") < 0 and m.find("*") < 0:
        delta_value = now_time_value - (int(h)*60 + int(m))
        if delta_value < 1 and delta_value > -1:
            return True
        else:
            return False
    if h.find("*") < 0:
        if m == "*":
            m_divider = 1
        else:
            m_divider = int(m.replace("*/", ""))
        delta_value = now_time_value - int(h)*60
        if delta_value % m_divider < 1:
            return True
        else:
            return False
    if m.find("*") < 0:
        if h == "*":
            h_divider = 60
        else:
            h_divider = int(h.replace("*/", ""))*60
        delta_value = now_time_value - int(m)
        if (delta_value % h_divider) < 1:
            return True
        else:
            return False
    else:
        if h == "*":
            h_divider = 60
        else:
            h_divider = int(h.replace("*/", ""))*60
        if m == "*":
            m_divider = 1
        else:
            m_divider = int(m.replace("*/", ""))
        delta_value = now_time_value % h_divider
        if delta_value < 60:
            if (delta_value % m_divider) < 1:
                return True
            else:
                return False
        else:
            return False
    return False

if __name__ == "__main__":
    configs = get_config.get_keyword_from_xml("config.xml")
    thread_array = []
    for config in configs:
        if need_thread_created_for_job(config["schedule"]):
            thread_entry = threading.Thread(target=run_thread, args=(config,))
            thread_entry.start()
            thread_array.append(thread_entry)
    for th in thread_array:
        th.join()
    if len(g_message) > 0:
        message_pusher.push_message("通知推送", g_message)
        #send_163_mail.send_163_mail(["70437407@qq.com"], "通知推送", g_message, [])
    #print g_message
