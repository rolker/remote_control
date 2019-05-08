#!/usr/bin/env python

# Roland Arsenault
# Center for Coastal and Ocean Mapping
# University of New Hampshire
# Copyright 2017, All rights reserved.

import sys
import socket
import struct
import datetime
import rospy
from geometry_msgs.msg import TwistStamped

address = '127.0.0.1'
port = 4242

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if '=' in arg:
            k,v = arg.split('=',1)
            if k == 'address':
                address = v
            if k == 'port':
                port = int(v)

pubs = {}

def remote_receiver():
    rospy.init_node('remote_receiver', anonymous=True)
    rate=rospy.Rate(20)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((address, port))
    
    while not rospy.is_shutdown():
        try:
            data,addr = sock.recvfrom(1024)
        except socket.error:
            break
        js_id,ts,ts_nsec,throttle,rudder = struct.unpack('!BIIdd',data)
        
        if not js_id in pubs:
            pubs[js_id] = rospy.Publisher('/remote/'+str(js_id)+'/cmd_vel',TwistStamped,queue_size=10)

        
        t = TwistStamped()
        t.twist.linear.x = throttle
        t.twist.angular.z = -rudder
        t.header.stamp.secs = ts
        t.header.stamp.nsecs = ts_nsec
    
        rospy.loginfo(t)
        pubs[js_id].publish(t)
        rate.sleep()

if __name__ == '__main__':
    try:
        remote_receiver()
    except rospy.ROSInterruptException:
        pass
    
