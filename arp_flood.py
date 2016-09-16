###################################################################################
# USAGE                                                                           #
# ------------------------------------------------------------------------------- #
# Run the script with following command line params in the following order        #
# 1. server ip                                                                    #
# 2. duration to be run                                                           #  
# 3. thread count of number packets to be sent simultaneously                     #
###################################################################################

import sys
import time
import threading
from scapy.all import sendp,srp,Ether,ARP,conf,Dot1Q,ls
import socket
import subprocess
from datetime import datetime
import random
src_ip = ""
mac_address = ""
dest_ip_list = []

def run_subprocess(command, check_error = False):
    p = subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    (output,err) = p.communicate()
    if check_error is True:
        return_value = p.returncode
        try:
            code = int(return_value)
            assert code == 0
        except Exception as ex:
            raise Exception("Failed in executing the command: " + str(command))
    return (output,err)

def get_mac_address(intf):
    mac_cmd = "cat /sys/class/net/" + intf + "/address"
    (stdout, stderr) = run_subprocess(command = mac_cmd, check_error = True)
    mac_addr = str(stdout.strip().lstrip().rstrip())
    return mac_addr

def get_interface_info(ip):
    interface_cmd = "netstat -ie | grep -B1 " + ip + " | head -n1 | awk {'print $1'}"
    (stdout, stderr) = run_subprocess(command = interface_cmd, check_error = True)
    intf = str(stdout.strip().lstrip().rstrip())
    mac_addr = get_mac_address(intf)
    return (intf, mac_addr)

def get_random_dest_ip(ip):
    host_number = int(ip.split(".")[-1])
    dest_host_list = list(set(range(1,255)) - set([host_number]))
    for host in dest_host_list:
        dest_ip = ".".join(ip.split(".")[:-1]) + "." + str(host)
        dest_ip_list.append(dest_ip)

def send_packet():
    random_dest_ip = random.choice(dest_ip_list)
    pkt = Ether(dst = "ff:ff:ff:ff:ff:ff", src = mac_address)
    pkt /= ARP(hwsrc = mac_address, psrc = src_ip, pdst = random_dest_ip)
    sendp(pkt, iface = "eth0");
    time.sleep(1)

def start_thread(thread_count):
    for i in range(thread_count):
        t = threading.Thread(target=send_packet)
        t.start()

if __name__ == '__main__':
    global src_ip
    src_ip = sys.argv[1]
    global mac_address
    interface, mac_address = get_interface_info(src_ip)
    get_random_dest_ip(src_ip)
    thread_count = int(sys.argv[3])
    time_duration = int(sys.argv[2])
    start_time = datetime.now()
    # print dest_ip_list
    print " src_ip:", src_ip, " mac_address:", mac_address, " duration:", time_duration, " thread_count:", thread_count
    while True:
        start_thread(thread_count)
        if int((datetime.now() - start_time).total_seconds()) > time_duration:
            break
        else:
            print("### ARP Flood in progress ###")
            print(int((datetime.now() - start_time).total_seconds()))
            time.sleep(1)
        