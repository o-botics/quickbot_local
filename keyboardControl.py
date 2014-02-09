#!/usr/local/bin/python2.7-32
"""
@brief Keyboard control for the QuickBot.

@description This program is used to drive the QuickBot via the keyboard

@author Rowland O'Flaherty (rowlandoflaherty.com)
@date 02/09/2014

@note Does not work with 64-bit python
This code was modified from http://www.pygame.org/docs/ref/joystick.html

@version: 1.0
@copyright: Copyright (C) 2014, Georgia Tech Research Corporation see the LICENSE file included with this software (see LINENSE file)
"""

import numpy as np
import pygame
import socket
import sys

# Constants
LEFT = 0
RIGHT = 1
FORWARD = 1
BACKWARD = -1

SEND_FLAG = True

UPDATE_TIMER = pygame.USEREVENT
SEND_TIMER = pygame.USEREVENT + 1

# Get input arguments
HOST = "192.168.1.101"
PORT = 5005
if len(sys.argv) > 2:
    print 'Invalid number of command line arguments.'
    print 'Proper syntax:'
    print '>> joystickControl.py robotIP'
    print 'Example:'
    print '>> QuickBotRun.py ', HOST
    sys.exit()

if len(sys.argv) == 2:
    HOST = sys.argv[1]

class QuickBot:
    # Parameters -- (LEFT, RIGHT)
    pwmMinVal = [45, 45]
    pwmMaxVal = [100, 100]

    # State -- (LEFT, RIGHT)
    pwm = [0.0, 0.0]
    pwmDelta = [2, 2]

    def __init__(self):
        if SEND_FLAG:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def stop(self):
        self.pwm = [0, 0]

    def update(self):
        # Slow down
        slowDownRate = 2
        for side in range(0,2):
            if self.pwm[side] > 0:
                self.accelerateByVal(-1*slowDownRate,side)
            elif self.pwm[side] < 0:
                self.accelerateByVal(slowDownRate,side)

    def accelerate(self,dir,side):
        self.accelerateByVal(dir*self.pwmDelta[side],side)

    def accelerateByVal(self,val,side):
        if self.pwm[side] == 0:
            self.pwm[side] = np.sign(val)*self.pwmMinVal[side]
        elif (self.pwm[side] == self.pwmMinVal[side] and np.sign(val) < 0) or \
            (self.pwm[side] == -1*self.pwmMinVal[side] and np.sign(val) > 0):
            self.pwm[side] = 0
        else:
            self.pwm[side] = self.pwm[side] + val

        if self.pwm[side] > 0:
            self.pwm[side] = min(self.pwm[side], self.pwmMaxVal[side])
        elif self.pwm[side] < 0:
            self.pwm[side] = max(self.pwm[side], -1*self.pwmMaxVal[side])

    def send(self):
        cmdStr = "$PWM=" +  str(QB.pwm[LEFT]) + "," + str(QB.pwm[RIGHT]) + "*\n"
        if SEND_FLAG:
            self.sock.sendto(cmdStr, (HOST, PORT))

QB = QuickBot()

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputing the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def printScreen(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()
pygame.key.set_repeat(10, 1)

# Set timers
pygame.time.set_timer(UPDATE_TIMER, 20) # Timer period in milliseconds
pygame.time.set_timer(SEND_TIMER, 200) # Timer period in milliseconds


# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("QuickBot Keyboard Control")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()


# Get ready to print
textPrint = TextPrint()

# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        elif event.type == UPDATE_TIMER:
            QB.update()
        elif event.type == SEND_TIMER:
            QB.send()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done=True
            elif event.key == pygame.K_SPACE:
                QB.stop()
            elif event.key == pygame.K_UP:
                QB.accelerate(FORWARD, LEFT)
                QB.accelerate(FORWARD, RIGHT)
            elif event.key == pygame.K_DOWN:
                QB.accelerate(BACKWARD, LEFT)
                QB.accelerate(BACKWARD, RIGHT)
            elif event.key == pygame.K_LEFT:
                QB.accelerate(BACKWARD, LEFT)
                QB.accelerate(FORWARD, RIGHT)
            elif event.key == pygame.K_RIGHT:
                QB.accelerate(FORWARD, LEFT)
                QB.accelerate(BACKWARD, RIGHT)


    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Print keyboard
    cmdStr = "QuickBot Command:"
    textPrint.printScreen(screen, cmdStr)
    cmdStr = "$PWM=" + str(QB.pwm[LEFT]) + "," + str(QB.pwm[RIGHT]) + "*\n"
    textPrint.printScreen(screen, cmdStr)


    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to N frames per second
    clock.tick(100)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
