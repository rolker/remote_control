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

joysticks = []

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

active = {}
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    if len(joysticks) == 0 and pygame.joystick.get_count()>0:
        for i in range(pygame.joystick.get_count()):
            js = pygame.joystick.Joystick(i)
            js.init()
            active[i]=False

            print js.get_name()

            naxes = js.get_numaxes()
            nbuttons = js.get_numbuttons()
            joysticks.append(js)

    now = datetime.datetime.utcnow()
    for js in joysticks:
        state = {'id':js.get_id(), 'timestamp':calendar.timegm(now.timetuple()), 'ts_nsec':now.microsecond*1000,'throttle':-apply_deadzone(js.get_axis(THROTTLE_AXIS))*2.75,'rudder':apply_deadzone(js.get_axis(RUDDER_AXIS))}
        
        b0 = js.get_button(0)
        if b0:
            active[state['id']] = True
        b1 = js.get_button(1)
        if b1:
            active[state['id']] = False
        
        print state['id'],'active:',active[state['id']],'throttle: {:%} rudder: {:%}'.format(state['throttle'],state['rudder'])
    
        if active[state['id']]:
            sock.sendto(struct.pack('!BIIdd',state['id'],state['timestamp'],state['ts_nsec'],state['throttle'],state['rudder']) ,(address,port))
    

    time.sleep(0.1)
