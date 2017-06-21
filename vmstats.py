#!/usr/bin/env python

# Copyright (c) 2009, Giampaolo Rodola'. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
A clone of iotop (http://guichaz.free.fr/iotop/) showing real time
disk I/O statistics.
It works on Linux only (FreeBSD and OSX are missing support for IO
counters).
It doesn't work on Windows as curses module is required.
Example output:
$ python scripts/iotop.py
Total DISK READ: 0.00 B/s | Total DISK WRITE: 472.00 K/s
PID   USER      DISK READ  DISK WRITE  COMMAND
13155 giampao    0.00 B/s  428.00 K/s  /usr/bin/google-chrome-beta
3260  giampao    0.00 B/s    0.00 B/s  bash
3779  giampao    0.00 B/s    0.00 B/s  gnome-session --session=ubuntu
3830  giampao    0.00 B/s    0.00 B/s  /usr/bin/dbus-launch
3831  giampao    0.00 B/s    0.00 B/s  //bin/dbus-daemon --fork --print-pid 5
3841  giampao    0.00 B/s    0.00 B/s  /usr/lib/at-spi-bus-launcher
3845  giampao    0.00 B/s    0.00 B/s  /bin/dbus-daemon
3848  giampao    0.00 B/s    0.00 B/s  /usr/lib/at-spi2-core/at-spi2-registryd
3862  giampao    0.00 B/s    0.00 B/s  /usr/lib/gnome-settings-daemon
Author: Giampaolo Rodola' <g.rodola@gmail.com>
"""

import atexit
import time
import sys

import psutil
import requests
import json

# --- curses stuff
def tear_down():
    win.keypad(0)


atexit.register(tear_down)
lineno = 0

def getCPUstate(interval=1):
    return (psutil.cpu_percent())

def getMemorystate():
        phymem = psutil.virtual_memory()
        line = "Memory: %5s%% %6s/%s"%(
            phymem.percent,
            str(int(phymem.used/1024/1024))+"M",
            str(int(phymem.total/1024/1024))+"M"
            )
        return line

# --- /curses stuff


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9.8 K/s'
    >>> bytes2human(100001221)
    '95.4 M/s'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.2f %s/s' % (value, s)
    return '%.2f B/s' % (n)


def poll(interval):
    """Calculate IO usage by comparing IO statics before and
    after the interval.
    Return a tuple including all currently running processes
    sorted by IO activity and total disks I/O activity.
    """
    # first get a list of all processes and disk io counters
    procs = [p for p in psutil.process_iter()]
    for p in procs[:]:
        try:
            p._before = p.io_counters()
        except psutil.Error:
            procs.remove(p)
            continue
    disks_before = psutil.disk_io_counters()
    tot_before = psutil.net_io_counters()
    pnic_before = psutil.net_io_counters(pernic=True)

    io_before = psutil.disk_io_counters()

    # sleep some time
    time.sleep(interval)
    tot_after = psutil.net_io_counters()
    pnic_after = psutil.net_io_counters(pernic=True)
        # io_after = psutil.disk_io_counters()

    io_tot_after = psutil.net_io_counters()
    io_pnic_after = psutil.net_io_counters(pernic=True)

        # get cpu state      
    cpu_state = getCPUstate(interval)
        # get memory      
    memory_state = getMemorystate()

    # then retrieve the same info again
    for p in procs[:]:
        with p.oneshot():
            try:
                p._after = p.io_counters()
                p._cmdline = ' '.join(p.cmdline())
                if not p._cmdline:
                    p._cmdline = p.name()
                p._username = p.username()
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                procs.remove(p)
    disks_after = psutil.disk_io_counters()

    # finally calculate results by comparing data before and
    # after the interval
    for p in procs:
        p._read_per_sec = p._after.read_bytes - p._before.read_bytes
        p._write_per_sec = p._after.write_bytes - p._before.write_bytes
        p._total = p._read_per_sec + p._write_per_sec

    disks_read_per_sec = disks_after.read_bytes - disks_before.read_bytes
    disks_write_per_sec = disks_after.write_bytes - disks_before.write_bytes

    # sort processes by total disk IO so that the more intensive
    # ones get listed first
    processes = sorted(procs, key=lambda p: p._total, reverse=True)

    return (processes, disks_read_per_sec, disks_write_per_sec, pnic_before, pnic_after,cpu_state,memory_state)


def refresh_window(procs, disks_read, disks_write, pnic_before, pnic_after,cpu_state,memory_state):
    """Print results on screen by using curses."""
    #curses.endwin()
    #templ = "%-5s %-7s %11s %11s  %s"
    #win.erase()

    #disks_tot = "Total DISK READ: %s | Total DISK WRITE: %s" \
    #            % (bytes2human(disks_read), bytes2human(disks_write))
    #print_line(disks_tot)

    #header = templ % ("PID", "USER", "DISK READ", "DISK WRITE", "COMMAND")
    
    #print_line(header, highlight=True)
    my_dict = {}
    read_sec = 0
    write_sec = 0

    for p in procs:
	read_sec = read_sec + p._read_per_sec
	write_sec = write_sec + p._write_per_sec

    read_sec = round(float(read_sec)/1024/128,2)
    write_sec = round(float(write_sec)/1024/128,2)
    # print read_sec, write_sec
    # print(cpu_state)

        # per-network interface details: let's sort network interfaces so      
        # that the ones which generated more traffic are shown first        
    nic_names = pnic_after.keys()
        #nic_names.sort(key=lambda x: sum(pnic_after[x]), reverse=True)       
    stats_before = pnic_before['eth5']
    stats_after = pnic_after['eth5']
    
    send_bytes = round(float(stats_after.bytes_sent - stats_before.bytes_sent)/1024/128,2)
    recv_bytes = round(float(stats_after.bytes_recv - stats_before.bytes_recv)/1024/128,2)
    # print 'net_send_bytes:' + str(send_bytes) + '/s'
    # print 'net_recv_bytes:' + str(recv_bytes) + '/s'
    # print("")
    my_dict['cpu'] = cpu_state
    my_dict['net_rx'] = recv_bytes
    my_dict['net_tx'] = send_bytes
    my_dict['io_read'] = read_sec
    my_dict['io_write'] = write_sec
    print my_dict
    requests.post('http://10.0.3.11:1984/attack/server_performance_data/1', data=json.dumps(my_dict))
    


def main():
    try:
        interval = 0
        while True:
            args = poll(interval)
            refresh_window(*args)
            interval = 1
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()
