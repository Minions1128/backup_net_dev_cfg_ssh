#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import time
import threading

from lib.net_device import DevInfo
from lib.net_device import NetDevice


dev_list_file = './dev_list.csv'


def get_dev_list(dev_list_file):
    '''
        Read the dev list from the 'dev_list_file', 
        'dev_list_file' has 4 attribute, use ',' to separate .
        4 attribute are dev hostname, ip address, brand and status.
        if status is 0, which means the dev is not avaiable.
    '''
    dev_list = []       # [DevInfo]
    with open(dev_list_file, 'r') as f:
        lines = f.readlines()
    for line in lines:
        item = line.split(",")
        if len(item) != 4:
            dev_list.append(DevInfo())
            continue
        hostname = item[0].split()[0] if len(item[0].split()) else None
        ip = item[1].split()[0] if len(item[1].split()) else None
        brand = item[2].split()[0] if len(item[2].split()) else None
        stat = item[3].split()[0] if len(item[3].split()) else False
        dev_list.append(DevInfo(hostname, ip, brand, stat))
    return dev_list


def get_dev_cfg(dev_info):
    global err_d
    
    dev = NetDevice(dev_info)
    dev.connect()
    try:
        dev.backup_cfg()
    except:
        err_d[dev.ip, dev.brand] = 'Cannot backup.'
        return
    if dev.log:
        err_d[dev.ip, dev.brand] = dev.log
    print dev_info.ip


def get_all_dev_cfg(dev_list, i):
    global lock
    global thread_c
    while True:
        lock.acquire()
        if dev_list:
            dev_info = dev_list.pop(0)
            lock.release()
        else:
            thread_c -= 1
            lock.release()
            break
        get_dev_cfg(dev_info)


def clear_old_data():
    os.system('rd/s/q cfg')       # windows
    os.system('mkdir cfg')


def main():
    clear_old_data()
    global lock
    global thread_c
    global err_d
    err_d = {}
    thread_c = 0
    lock = threading.Lock()
    dev_list = get_dev_list(dev_list_file) # from the dev_list.csv
    thread_num = 8
    for i in range(thread_num):
        thread_c += 1
        t = threading.Thread(target=get_all_dev_cfg, args=(dev_list,i,))
        t.start()
    while thread_c > 0:
        time.sleep(0.1)
    summ = {}
    for err in err_d:
        summ.setdefault(err_d[err], [])
        summ[err_d[err]].append(err)
    print summ
    with open('./cfg/_log.txt', 'w') as f:
        f.write(str(err_d))
        f.write('\n\n\n')
        f.write(str(summ))


if __name__ == '__main__':
    main()
