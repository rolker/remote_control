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

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    now = datetime.datetime.utcnow()
    state = {'timestamp':calendar.timegm(now.timetuple())+now.microsecond/1000000.0 ,'throttle':-js.get_axis(THROTTLE_AXIS),'rudder':js.get_axis(RUDDER_AXIS)}
        
    print state
    
    sock.sendto(struct.pack('!ddd',state['timestamp'],state['throttle'],state['rudder']) ,(address,port))
    

    time.sleep(0.05)
