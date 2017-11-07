#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import paramiko


usr = 'admin'
psw = 'password'
folder_path = '.\\cfg\\'


class NetDevice(object):
    def __init__(self, dev, *args, **kwargs):
        super(NetDevice, self).__init__()
        self.ip = dev.ip
        self.brand = dev.brand
        self.hostname = dev.hostname
        self.stat = dev.stat
        self.now = today = time.strftime("%y%m%d", time.localtime())
        self.log = {}


    def connect(self, port=22):
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(self.ip, port, usr, psw, allow_agent=False, look_for_keys=False)
        except Exception as err:
            self.log = 'Cannot access.'
            return


    def file_save(self, config=None):
        file_path = folder_path + "{}_{}_{}.cfg".format(self.hostname, self.ip, self.now)
        with open(file_path, 'w') as f:
            f.write(config)


    def backup_cfg(self):
        if self.stat == '0':
            self.log = 'Stat is 0'
            return
        if self.brand == 'Cisco':
            config = self.show_run()
        elif self.brand == 'H3C':
            config = self.dis_cu()
        elif self.brand == 'Juniper':
            config = self.show_conf()
        else:
            self.log = 'Bad brand'
            return
        self.file_save(config)


    def show_run(self):
        channel = self.ssh.invoke_shell()
        channel.settimeout(8)
        channel.send('terminal length 0')
        channel.send('\n')
        channel.send('sh run')
        channel.send('\n')
        buff = ''
        while not buff.endswith("#"):
            time.sleep(1)
            resp = channel.recv(9999)
            buff += resp
        return buff


    def dis_cu(self):
        channel = self.ssh.invoke_shell()
        channel.settimeout(8)
        channel.send('\n\n\n')
        channel.send('screen-length disable')
        channel.send('\n')
        channel.send('dis cu')
        channel.send('\n')
        buff = ''
        while not buff.endswith(">"):
            time.sleep(1)
            resp = channel.recv(9999)
            buff += resp
        return buff


    def show_conf(self):
        channel = self.ssh.invoke_shell()
        channel.settimeout(8)
        channel.send('show configuration | display set | no-more\n')
        buff = ''
        while not buff.endswith("> "):
            time.sleep(1)
            resp = channel.recv(9999)
            buff += resp
        return buff



class DevInfo(object):
    def __init__(self, hostname=None, ip=None, brand=None, stat=False):
        super(DevInfo, self).__init__()
        self.ip = ip
        self.hostname = hostname
        self.brand = brand
        self.stat = stat if (self.ip and self.hostname and self.brand) else False


    @staticmethod
    def ping(ip):
        # return os.system("ping -c 3 -W 3 %s" % (ip))  # linux
        return os.system("ping -n 3 %s" % (ip))         # Windows


    @staticmethod
    def is_ip(host):
        if not host or not type(host) in [str, unicode]:
            return False
        re_str = ur"^([1-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])(\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])){3}$"    
        ptn = re.compile(re_str, flags=re.S|re.I|re.M)
        return True if ptn.findall(host) else False
