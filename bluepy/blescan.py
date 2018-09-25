#!/usr/bin/env python
from __future__ import print_function
import argparse
import binascii
import os
import sys
from bluepy import btle
import pprint as pp
import randomize

bluetooth_devices = {}
bluetooth_device_all = {}

if os.getenv('C', '1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_OFF = ANSI_CSI + '0m'

def create_dev_tree(bluetooth_devices):
    conn = 0
    non_conn = 0

    c_manuf = 0
    c_m_rand = 0
    c_m_pub = 0
    c_m_r_nam = 0
    c_m_r_unam = 0
    c_m_p_nam = 0
    c_m_p_unam = 0


    c_non_manuf = 0
    c_nm_rand = 0
    c_nm_pub = 0
    c_nm_r_nam = 0
    c_nm_r_unam = 0
    c_nm_p_nam = 0
    c_nm_p_unam = 0


    for key, val in bluetooth_devices.items():
        if val['conn'] == 'connectable':
            conn +=1

            if val['manufacturer'] == None:
                c_non_manuf += 1
                if val['addr_type'] == 'public':
                    c_nm_pub += 1
                    if val['name'] == None:
                        c_mm_p_unam += 1
                    else:
                        c_nm_p_nam += 1
                elif val['addr_type'] == 'random':
                    c_m_rand += 1
                    if val['name'] == None:
                        c_nm_r_unam += 1
                    else:
                        c_nm_r_nam += 1
            else:
                c_manuf += 1
                if val['addr_type'] == 'public':
                    c_m_pub += 1
                    if val['name'] == None:
                        c_m_p_unam += 1
                    else:
                        c_m_p_nam += 1
                elif val['addr_type'] == 'random':
                    c_m_rand += 1
                    if val['name'] == None:
                        c_m_r_unam += 1
                    else:
                        c_m_r_nam += 1


        else:
            non_conn +=1

    print ("conn: ", conn)
    print ("\tmanufacturer: ", c_manuf)
    print ("\t\trandom: ", c_m_rand)
    print ("\t\t\tnamed: ", c_m_r_nam)
    print ("\t\t\tunnamed: ", c_m_r_unam)
    print ("\t\tpublic: ", c_m_pub)
    print ("\t\t\tnamed: ", c_m_p_nam)
    print ("\t\t\tunnamed: ", c_m_p_unam)
    print ("\tnon manufacturer: ", c_non_manuf)
    print ("\t\trandom: ", c_nm_rand)
    print ("\t\t\tnamed: ", c_nm_r_nam)
    print ("\t\t\tunnamed: ", c_nm_r_unam)
    print ("\t\tpublic: ", c_nm_pub)
    print ("\t\t\tnamed: ", c_nm_p_nam)
    print ("\t\t\tunnamed: ", c_nm_p_unam)
    print ("non conn", non_conn)


def printInfo(bt_devices):
    n_conn = 0
    n_non_conn = 0
    n_non_manufacturer = 0
    n_manufacturer = 0
    n_random = 0
    n_public = 0
    n_named = 0
    n_unnamed = 0

    for key, value in bt_devices.items():
        
        if value['conn'] == 'connectable':
            n_conn +=1 
        else:
            n_non_conn +=1

        if value['manufacturer'] == None:
            n_non_manufacturer += 1
        else:
            n_manufacturer += 1

        if value['addr_type'] == 'random':
            n_random +=1
        else:
            n_public +=1

        if value['name'] == None:
            n_unnamed += 1
        else:
            n_named += 1

    print("Total devices \"unique\": ", len(bluetooth_devices))
    print("Total device all", len(bluetooth_device_all))
    print('conn, non conn:', n_conn, n_non_conn)
    print('manu, non manu:', n_non_manufacturer, n_manufacturer)
    print('random, public:', n_random, n_public)
    print('named, unnamed', n_named, n_unnamed)

def dump_services(dev):
    services = sorted(dev.services, key=lambda s: s.hndStart)
    for s in services:
        print ("\t%04x: %s" % (s.hndStart, s))
        if s.hndStart == s.hndEnd:
            continue
        chars = s.getCharacteristics()
        for i, c in enumerate(chars):
            props = c.propertiesToString()
            h = c.getHandle()
            if 'READ' in props:
                val = c.read()
                if c.uuid == btle.AssignedNumbers.device_name:
                    string = ANSI_CYAN + '\'' + \
                        val.decode('utf-8') + '\'' + ANSI_OFF
                elif c.uuid == btle.AssignedNumbers.device_information:
                    string = repr(val)
                else:
                    string = '<s' + binascii.b2a_hex(val).decode('utf-8') + '>'
            else:
                string = ''
            print ("\t%04x:    %-59s %-12s %s" % (h, c, props, string))

            while True:
                h += 1
                if h > s.hndEnd or (i < len(chars) - 1 and h >= chars[i + 1].getHandle() - 1):
                    break
                try:
                    val = dev.readCharacteristic(h)
                    print ("\t%04x:     <%s>" %
                           (h, binascii.b2a_hex(val).decode('utf-8')))
                except btle.BTLEException:
                    break


class ScanPrint(btle.DefaultDelegate):

    def __init__(self, opts):
        btle.DefaultDelegate.__init__(self)
        self.opts = opts

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            status = "new"
            devName = None
        elif isNewData:
            if self.opts.new:
                return
            status = "update"
            return
        else:
            if not self.opts.all:
                return
            status = "old"

        if dev.rssi < self.opts.sensitivity:
            return

        
        print ('    Device (%s): %s (%s), %d dBm %s' %
               (status,
                   ANSI_WHITE + dev.addr + ANSI_OFF,
                   dev.addrType,
                   dev.rssi,
                   ('(connectable)' if dev.connectable else '(not connectable)'))
               )
        

        for (sdid, desc, val) in dev.getScanData():
            if sdid in [8, 9]:
                print ('\t' + desc + ': \'' + ANSI_CYAN + val + ANSI_OFF + '\'')
                devName = (val if 'Name' in desc else None)
            else:
                print ('\t' + desc + ': <' + val + '>')
                manufacturer = (val if 'Manufacturer' in desc else None)
 
        if not dev.scanData:
            print ('\t(no data)')
                #store devices


        siblings = randomize.generate_possible_siblings(dev.addr)

        is_in = False
        in_list = []

        bluetooth_device_all[dev.addr] = \
                {'rssi': dev.rssi,
                 'conn': ('connectable' if dev.connectable else 'not connectable'),
                 'addr_type': dev.addrType,
                 'manufacturer': manufacturer, 
                 'name': devName
                 }

        for mac in siblings:
            if mac in bluetooth_devices:
                is_in = True
                mac_father = mac
        
        if not is_in:
            bluetooth_devices[dev.addr] = \
                {'rssi': dev.rssi,
                 'conn': ('connectable' if dev.connectable else 'not connectable'),
                 'addr_type': dev.addrType,
                 'manufacturer': manufacturer, 
                 'name': devName,
                 'derivate': []} 
        else:
           bluetooth_devices[mac_father]['derivate'].append(dev.addr)

        print


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--hci', action='store', type=int, default=0,
                        help='Interface number for scan')
    parser.add_argument('-t', '--timeout', action='store', type=int, default=4,
                        help='Scan delay, 0 for continuous')
    parser.add_argument('-s', '--sensitivity', action='store', type=int, default=-128,
                        help='dBm value for filtering far devices')
    parser.add_argument('-d', '--discover', action='store_true',
                        help='Connect and discover service to scanned devices')
    parser.add_argument('-a', '--all', action='store_true',
                        help='Display duplicate adv responses, by default show new + updated')
    parser.add_argument('-n', '--new', action='store_true',
                        help='Display only new adv responses, by default show new + updated')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity')
    arg = parser.parse_args(sys.argv[1:])

    btle.Debugging = arg.verbose

    scanner = btle.Scanner(arg.hci).withDelegate(ScanPrint(arg))

    print (ANSI_RED + "Scanning for devices..." + ANSI_OFF)
    devices = scanner.scan(arg.timeout)

    if arg.discover:
        print (ANSI_RED + "Discovering services..." + ANSI_OFF)

        for d in devices:
            if not d.connectable:

                continue

            print ("    Connecting to", ANSI_WHITE + d.addr + ANSI_OFF + ":")

            dev = btle.Peripheral(d)
            dump_services(dev)
            dev.disconnect()
            print

if __name__ == "__main__":
    main()
    pp.pprint(bluetooth_devices)
    printInfo(bluetooth_devices)

    create_dev_tree(bluetooth_devices)
