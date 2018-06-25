#!/usr/bin/env python

# Roland Arsenault
# Center for Coastal and Ocean Mapping
# University of New Hampshire
# Copyright 2017, All rights reserved.


import sys
import pygame
import datetime
import calendar
import time
import socket
import struct

pygame.init()

THROTTLE_AXIS = 1
RUDDER_AXIS = 3



size = (320, 240)
screen = pygame.display.set_mode(size)

js = None

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = '127.0.0.1'
port = 4242
deadzone = 0.1

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if '=' in arg:
            k,v = arg.split('=',1)
            if k == 'address':
                address = v
            if k == 'port':
                port = int(v)
            if k == 'deadzone':
                deadzone = float(v)
        
def apply_deadzone(value):
    sign = 1
    if value < 0:
        sign = -1
    magnitude = abs(value)
    if magnitude < deadzone:
        magnitude = 0.0
    else:
        magnitude = (magnitude-deadzone)/(1.0-deadzone)
    return magnitude*sign

active = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    if js is None and pygame.joystick.get_count()>0:
        js = pygame.joystick.Joystick(0)
        js.init()

        print js.get_name()

        naxes = js.get_numaxes()
        nbuttons = js.get_numbuttons()



    now = datetime.datetime.utcnow()
    if js is not None:
        state = {'timestamp':calendar.timegm(now.timetuple()), 'ts_nsec':now.microsecond*1000,'throttle':-apply_deadzone(js.get_axis(THROTTLE_AXIS)),'rudder':apply_deadzone(js.get_axis(RUDDER_AXIS))}
        
        b0 = js.get_button(0)
        if b0:
            active = True
        b1 = js.get_button(1)
        if b1:
            active = False
    else:
        state = {'timestamp':calendar.timegm(now.timetuple()), 'ts_nsec':now.microsecond*1000,'throttle':0.0,'rudder':0.0}
        
    print 'active:',active,'throttle: {:%} rudder: {:%}'.format(state['throttle'],state['rudder'])
    
    if active:
        sock.sendto(struct.pack('!IIdd',state['timestamp'],state['ts_nsec'],state['throttle'],state['rudder']) ,(address,port))
    

    time.sleep(0.05)
