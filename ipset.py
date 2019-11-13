# !/usr/bin/python3

import os
import constant
import configparser
config = configparser.ConfigParser()
file = constant.configFile

#set ip eth0
def ipset():
    config.read(file)
    readip = config['device']['ip']
    netmask = config['device']['netmask']
    os.system('sudo ifconfig eth0 {0} netmask {1} up'.format(readip,netmask))
    print('ip eth0: {0}, netmask eth0:{1}'.format(readip,netmask))

def netmaskset():
    config.read(file)
    netmask = config['device']['netmask']
    os.system('sudo ifconfig eth0 netmask {}'.format(netmask))
    print('netmask eth0: %s'% netmask)

def gatewayset():
    config.read(file)
    readip = config['device']['ip']
    gateway = config['device']['gateway']
    print('gw eth0: %s'% gateway)
    os.system('sudo route del default')
    os.system('sudo route del default')
    #os.system('sudo ip route delete 10.10.214.0/24')
    #os.system('sudo ip route delete 10.10.214.0/24')
    #os.system('sudo ip route delete 169.254.0.0/16')
    os.system('sudo ip route add 10.10.214.0/24 via {}'.format(readip))
    os.system('sudo route add default gw {}'.format(gateway))

ipset()
#netmaskset()
gatewayset()
