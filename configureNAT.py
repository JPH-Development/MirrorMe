import os
import sys
import fileinput
import subprocess as sub

def execute():
    configure()
    enablePersistantState()
    startRouter() 

#configure the NAT to link the ethernet and wireless card allowing internet access. 
def configure():
    filedata = None
    pathName = '/etc/sysctl.conf'

    #check file path exists
    if not os.path.isfile(pathName):
        print("file doesn't exist")
        sys.exit(1)

    #append file with ip forwarding
    with open(pathName, 'a') as file:
        file.write("net.ipv4.ip_forward=1")
        print("ip forwarding added")

    print("start translation for ip..") 
    #make Linux command call to start translation
    sub.Popen(['sudo', 'sh', '-c', '"echo 1 > /proc/sys/net/ipv4/ip_forward"' ],
                    stdout=sub.PIPE, stderr=sub.PIPE)

    #set up translation between ethernet port and wirless card
    print("Setting up translation between ethernet and wireless..")
    sub.Popen(['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', '-j', 'MASQUERADE'],
                    stdout=sub.PIPE, stderr=sub.PIPE)
    sub.Popen(['sudo', 'iptables', '-A', 'FORWARD', '-i', 'eth0', '-o', 'wlan0', '-m', 'state',
               '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'],
                    stdout=sub.PIPE, stderr=sub.PIPE)
    sub.Popen(['sudo', 'iptables', '-A', 'FORWARD', '-i', 'wlan0', '-o', 'eth0', '-j', 'ACCEPT'],
                    stdout=sub.PIPE, stderr=sub.PIPE)
    print("configure NAT completed") 

#during raspberry pi restarts keep the network enabled. 
def enablePersistantState():
    filedata = None
    oldpath = '/etc/rc.local'
    newPath = './rc.local'

    print("enabling persistant state...") 
    #Backup NAT configuration
    sub.Popen(['sudo', 'sh', '-c', '"iptables-save > /etc/iptables.ipv4.nat"' ],
                    stdout=sub.PIPE, stderr=sub.PIPE)
    
    #Restore configuration when network comes up
    if not os.path.isfile(oldpath):
        print("can't find rc.local file")
        sys.exit(1)
    if not os.path.isfile(newPath):
        print "can't find new rc.local file"
    
    
    with open(newPath, 'r') as file:
        filedata = file.read()
        print("read config changes")
    with open(oldPath, 'w') as file:
        file.write(filedata)
        print "wrote changes to rc.local file"

    print("persistant state enabled") 

def startRouter():
    #Start wireless router
    print("wirless router starting..") 
    sub.Popen(['sudo', 'service', 'hostapd', 'start'],
                    stdout=sub.PIPE, stderr=sub.PIPE)
    sub.Popen(['sudo', 'service', 'dnsmasq', 'start'],
                    stdout=sub.PIPE, stderr=sub.PIPE)
    print "started router"
