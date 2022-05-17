
import os
import sys
import time
import subprocess
import re
import socket
import fcntl
import struct
import threading
import signal
import argparse
import logging
import logging.handlers
import random
import string
import base64
import hashlib
import binascii
import urllib.request
import urllib.parse
import urllib.error
import http.client
import ssl
import select
import getpass
import netifaces
import netaddr

class WifiHacking(object):
    def __init__(self):
        self.__version__ = "1.0.0"
        self.__author__ = "N0b0dy"
        self.__email__ = "bermejo.genesis02@gmail.com"
        self.__license__ = "GPLv3"
        self.__description__ = "Wifi hacking tool"
        self.__logger__ = logging.getLogger("WifiHacking")
        self.__logger__.setLevel(logging.DEBUG)
        self.__logger__.addHandler(logging.StreamHandler())
        self.__logger__.addHandler(logging.handlers.SysLogHandler(address = '/dev/log'))
        self.__logger__.addHandler(logging.handlers.SysLogHandler(address = '/dev/log',facility = logging.handlers.SysLogHandler.LOG_LOCAL2))

    def Interface(self, ifname):
        return {
            "name": ifname,
            "mac": self.__get_interface_mac__(ifname),
            "ip": self.__get_interface_ip__(ifname),
            "netmask": self.__get_interface_netmask__(ifname),
            "broadcast": self.__get_interface_broadcast__(ifname),
            "gateway": self.__get_interface_gateway__(ifname),
            "dns": self.__get_interface_dns__(ifname),
            "network": self.__get_interface_network__(ifname),
            "netmask_cidr": self.__get_interface_netmask_cidr__(ifname),
            "ssid": self.__get_ssid__(ifname),
            "channel": self.__get_channel__(ifname),
            "encryption": self.__get_encryption__(ifname),
            "signal": self.__get_signal__(ifname),
            "bitrate": self.__get_bitrate__(ifname),
            "mode": self.__get_mode__(ifname),
            "frequence": self.__get_frequence__(ifname),
            "txpower": self.__get_txpower__(ifname),
            "retry": self.__get_retry__(ifname),
            "rts": self.__get_rts__(ifname),
            "frag": self.__get_frag__(ifname),
            "power": self.__get_power__(ifname),
            "noise": self.__get_noise__(ifname),
            "retry": self.__get_retry__(ifname),
            "rts": self.__get_rts__(ifname),
        }
        if self.__get_interface_mac__(ifname) == "00:00:00:00:00:00":
            return None
        else:
            return self.Interface(ifname)
        
        print(self.__get_interface_list__())
        print(self.__get_interface_info__("wlan0"))
        print(self.__get_interface_mac__("wlan0"))
        print(self.__get_interface_ip__("wlan0"))
        print(self.__get_interface_netmask__("wlan0"))
        print(self.__get_interface_broadcast__("wlan0"))
        print(self.__get_interface_gateway__("wlan0"))
        print(self.__get_interface_dns__("wlan0"))
        print(self.__get_interface_network__("wlan0"))
        print(self.__get_interface_netmask_cidr__("wlan0"))
        print(self.__get_ssid__("wlan0"))
        print(self.__get_channel__("wlan0"))
        print(self.__get_encryption__("wlan0"))
        print(self.__get_signal__("wlan0"))
        print(self.__get_bitrate__("wlan0"))
        print(self.__get_mode__("wlan0"))
        print(self.__get_frequence__("wlan0"))
        print(self.__get_txpower__("wlan0"))
        print(self.__get_retry__("wlan0"))
        print(self.__get_rts__("wlan0"))
        print(self.__get_frag__("wlan0"))
        print(self.__get_power__("wlan0"))
        print(self.__get_noise__("wlan0"))
        print(self.__get_retry__("wlan0"))


    def __get_mac_address__(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
        return ':'.join(['%02x' % ord(char) for char in info[18:24]])
    
    def __get_ip_address__(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])

    def __get_ssid__(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8192, struct.pack('256s', ifname[:15]))
        return ''.join(['%02x' % ord(char) for char in info[26:36]]).strip('\x00')

    def __get_channel__(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8192, struct.pack('256s', ifname[:15]))
        return ord(info[36:37])

    def __get_signal_strength__(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8192, struct.pack('256s', ifname[:15]))
        return ord(info[37:38])

    def __get_bssid__(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8192, struct.pack('256s', ifname[:15]))
        return ''.join(['%02x' % ord(char) for char in info[46:54]]).strip('\x00')

    def __get_interface_list__(self):
        return netifaces.interfaces()

    def __get_interface_info__(self, ifname):
        return netifaces.ifaddresses(ifname)

    def __get_interface_mac__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_LINK][0]['addr']

    def __get_interface_ip__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_INET][0]['addr']

    def __get_interface_netmask__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_INET][0]['netmask']

    def __get_interface_broadcast__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_INET][0]['broadcast']

    def __get_interface_gateway__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_INET][0]['gateway']
    
    def __get_interface_dns__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_INET][0]['dns']
    
    def __get_interface_netmask__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_INET][0]['netmask']

    def __get_interface_netmask_cidr__(self, ifname):
        return netaddr.IPNetwork(self.__get_interface_netmask__(ifname)).netmask_bits()

    def __get_interface_network__(self, ifname):
        return self.__get_interface_info__(ifname)[netifaces.AF_INET][0]['network']

    def NetworkInfo(self, ifname):
        self.__logger__.info("[+] Network info for interface %s" % ifname)
        self.__logger__.info("[+] MAC Address: %s" % self.__get_interface_mac__(ifname))
        self.__logger__.info("[+] IP Address: %s" % self.__get_interface_ip__(ifname))
        self.__logger__.info("[+] Netmask: %s" % self.__get_interface_netmask__(ifname))
        self.__logger__.info("[+] Netmask CIDR: %s" % self.__get_interface_netmask_cidr__(ifname))
        self.__logger__.info("[+] Network: %s" % self.__get_interface_network__(ifname))
        self.__logger__.info("[+] Broadcast: %s" % self.__get_interface_broadcast__(ifname))
        self.__logger__.info("[+] Gateway: %s" % self.__get_interface_gateway__(ifname))
        self.__logger__.info("[+] DNS: %s" % self.__get_interface_dns__(ifname))
        print("[+] Network info for interface %s" % ifname)
        print("[+] MAC Address: %s" % self.__get_interface_mac__(ifname))
        print("[+] IP Address: %s" % self.__get_interface_ip__(ifname))
        print("[+] Netmask: %s" % self.__get_interface_netmask__(ifname))
        print("[+] Netmask CIDR: %s" % self.__get_interface_netmask_cidr__(ifname))
        print("[+] Network: %s" % self.__get_interface_network__(ifname))
        print("[+] Broadcast: %s" % self.__get_interface_broadcast__(ifname))
        print("[+] Gateway: %s" % self.__get_interface_gateway__(ifname))
        print("[+] DNS: %s" % self.__get_interface_dns__(ifname))
        return True
    
    def __main__(self):
        parser = argparse.ArgumentParser(description = self.__description__, formatter_class = argparse.RawTextHelpFormatter)
        parser.add_argument('-v', '--version', action = 'version', version = self.__description__ + " " + self.__version__)
        parser.add_argument('-a', '--all', action = 'store_true', help = 'Show all information')
        parser.add_argument('-i', '--interface', action = 'store', help = 'Interface name')
        parser.add_argument('-m', '--mac', action = 'store_true', help = 'Show MAC address')
        parser.add_argument('-s', '--ssid', action = 'store_true', help = 'Show SSID')
        parser.add_argument('-c', '--channel', action = 'store_true', help = 'Show channel')
        parser.add_argument('-r', '--signal', action = 'store_true', help = 'Show signal strength')
        parser.add_argument('-b', '--bssid', action = 'store_true', help = 'Show BSSID')
        parser.add_argument('-n', '--network', action = 'store_true', help = 'Show network')
        parser.add_argument('-g', '--gateway', action = 'store_true', help = 'Show gateway')
        parser.add_argument('-d', '--dns', action = 'store_true', help = 'Show DNS')
        parser.add_argument('-w', '--netmask', action = 'store_true', help = 'Show netmask')
        parser.add_argument('-x', '--netmask_cidr', action = 'store_true', help = 'Show netmask CIDR')
        parser.add_argument('-y', '--network', action = 'store_true', help = 'Show network')
        parser.add_argument('-e', '--interface_list', action = 'store_true', help = 'Show interface list')
        parser.add_argument('-z', '--interface_info', action = 'store', help = 'Show interface information')
        parser.add_argument('-t', '--interface_mac', action = 'store', help = 'Show interface MAC address')
        parser.add_argument('-u', '--interface_ip', action = 'store', help = 'Show interface IP address')
        parser.add_argument('-o', '--interface_netmask', action = 'store', help = 'Show interface netmask')
        parser.add_argument('-p', '--interface_netmask_cidr', action = 'store', help = 'Show interface netmask CIDR')
        parser.add_argument('-q', '--interface_network', action = 'store', help = 'Show interface network')
        parser.add_argument('-f', '--interface_broadcast', action = 'store', help = 'Show interface broadcast')
        parser.add_argument('-j', '--interface_gateway', action = 'store', help = 'Show interface gateway')
        parser.add_argument('-k', '--interface_dns', action = 'store', help = 'Show interface DNS')
        args = parser.parse_args()
        if args.all:
            self.__show_all__(args.interface)
        elif args.mac:
            self.__show_mac__(args.interface)
        elif args.ssid:
            self.__show_ssid__(args.interface)
        elif args.channel:
            self.__show_channel__(args.interface)
        elif args.signal:
            self.__show_signal__(args.interface)
        elif args.bssid:
            self.__show_bssid__(args.interface)
        elif args.network:
            self.__show_network__(args.interface)
        elif args.gateway:
            self.__show_gateway__(args.interface)
        elif args.dns:
            self.__show_dns__(args.interface)
        elif args.netmask:
            self.__show_netmask__(args.interface)
        elif args.netmask_cidr:
            self.__show_netmask_cidr__(args.interface)
        elif args.network:
            self.__show_network__(args.interface)   
        elif args.interface_list:   
            self.__show_interface_list__()
        elif args.interface_info:
            self.__show_interface_info__(args.interface_info)
        elif args.interface_mac:
            self.__show_interface_mac__(args.interface_mac)
        elif args.interface_ip:
            self.__show_interface_ip__(args.interface_ip)
        elif args.interface_netmask:
            self.__show_interface_netmask__(args.interface_netmask)
        elif args.interface_netmask_cidr:
            self.__show_interface_netmask_cidr__(args.interface_netmask_cidr)
        elif args.interface_network:
            self.__show_interface_network__(args.interface_network)
        elif args.interface_broadcast:
            self.__show_interface_broadcast__(args.interface_broadcast)
        elif args.interface_gateway:
            self.__show_interface_gateway__(args.interface_gateway)
        elif args.interface_dns:
            self.__show_interface_dns__(args.interface_dns)
        else:
            parser.print_help()
        
if __name__ == '__main__':
    iface = Interface()
    iface.__main__()

