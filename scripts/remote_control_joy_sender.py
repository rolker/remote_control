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

js = pygame.joystick.Joystick(0)
js.init()

print js.get_name()

naxes = js.get_numaxes()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

address = '127.0.0.1'
port = 4242
deadzone = 0.1

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


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    now = datetime.datetime.utcnow()
    state = {'timestamp':calendar.timegm(now.timetuple()), 'ts_nsec':now.microsecond*1000,'throttle':-apply_deadzone(js.get_axis(THROTTLE_AXIS)),'rudder':apply_deadzone(js.get_axis(RUDDER_AXIS))}
        
    print 'throttle: {:%} rudder: {:%}'.format(state['throttle'],state['rudder'])
    
    sock.sendto(struct.pack('!IIdd',state['timestamp'],state['ts_nsec'],state['throttle'],state['rudder']) ,(address,port))
    

    time.sleep(0.05)
