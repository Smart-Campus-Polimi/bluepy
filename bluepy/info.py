#!/usr/bin/env python
import os, errno
import csv

def create_dev_tree(bt_devices):
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


    for key, val in bt_devices.items():
        if val['conn'] == 'connectable':
            conn +=1

            if val['manufacturer'] == None:
                c_non_manuf += 1
                if val['addr_type'] == 'public':
                    c_nm_pub += 1
                    if val['name'] == None:
                        c_nm_p_unam += 1
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


    print "conn: ", conn
    print "\tmanufacturer: ", c_manuf
    print "\t\trandom: ", c_m_rand
    print "\t\t\tnamed: ", c_m_r_nam
    print "\t\t\tunnamed: ", c_m_r_unam
    print "\t\tpublic: ", c_m_pub
    print "\t\t\tnamed: ", c_m_p_nam
    print "\t\t\tunnamed: ", c_m_p_unam
    print "\tnon manufacturer: ", c_non_manuf
    print "\t\trandom: ", c_nm_rand
    print "\t\t\tnamed: ", c_nm_r_nam
    print "\t\t\tunnamed: ", c_nm_r_unam
    print "\t\tpublic: ", c_nm_pub
    print "\t\t\tnamed: ", c_nm_p_nam
    print "\t\t\tunnamed: ", c_nm_p_unam
    print "non conn", non_conn

    return [conn, c_manuf, c_m_rand, c_m_r_nam, c_m_r_unam, c_m_pub, c_m_p_nam, c_m_p_unam, 
    		c_non_manuf, c_nm_rand, c_nm_r_nam, c_nm_r_unam, c_nm_pub, c_nm_p_nam, c_nm_p_unam, non_conn]

def create_directory(directory_path):
	try:
		print "directory path", directory_path
		os.makedirs(os.path.expanduser(directory_path))
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	return directory_path

def create_csv(name):
	with open(os.path.expanduser(name), 'w') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(['timestamp', 'real_people','non_connectable','connectable',
										'con_manufacturer', 'con_man_random', 'con_man_rand_named', 'con_man_rand_unnamed',
										'con_man_public', 'con_man_pub_named', 'con_man_pub_unnamed',
										'con_nonmanufactured', 'con_nonman_random', 'con_nonman_rand_named', 'con_nonman_rand_unnamed',
										'con_nonman_public', 'con_nonman_pub_named', 'con_nonman_pub_unnamed'])

	return name

def write_data(bt_list, people, ts, name):
	bt_list.insert(0, int(people))
	bt_list.insert(0, str(ts)[:-7])


	with open(os.path.expanduser(name), 'a') as csvfile:
		filewriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
		filewriter.writerow(bt_list)

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

    print "Total devices \"unique\": ", len(bt_devices)
    print "Total device all", len(bt_devices)
    print 'conn, non conn:', n_conn, n_non_conn
    print 'manu, non manu:', n_non_manufacturer, n_manufacturer
    print 'random, public:', n_random, n_public
    print 'named, unnamed', n_named, n_unnamed