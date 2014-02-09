#!/usr/local/bin/python2.7-32
"""
@brief Joystick control for the QuickBot.

@description This program is used to drive the QuickBot via a joystick (actually gamepad).
Currently setup for tank drive.

@author Rowland O'Flaherty (rowlandoflaherty.com)
@date 12/10/2013

@note Does not work with 64-bit python

@version: 1.0
@copyright: Copyright (C) 2014, Georgia Tech Research Corporation see the LICENSE file included with this software (see LINENSE file)
"""

import pygame
import socket
import sys

sendFlag = True

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

if sendFlag:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()

# Get ready to print
textPrint = TextPrint()

# -------- Main Program Loop -----------
while done==False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop

        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        # if event.type == pygame.JOYBUTTONDOWN:
        #     print("Joystick button pressed.")
        # if event.type == pygame.JOYBUTTONUP:
        #     print("Joystick button released.")


    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    textPrint.printScreen(screen, "Number of joysticks: {}".format(joystick_count) )
    textPrint.indent()
    axis = [0]*4
    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        textPrint.printScreen(screen, "Joystick {}".format(i) )
        textPrint.indent()

        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.printScreen(screen, "Joystick name: {}".format(name) )

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.printScreen(screen, "Number of axes: {}".format(axes) )
        textPrint.indent()

        for i in range( axes ):
            axis[i] = joystick.get_axis( i )
            textPrint.printScreen(screen, "Axis {} value: {:>6.3f}".format(i, axis[i]) )
            pwm = int(-100*axis[i])
            if pwm > -20 and pwm < 20:
                pwm = 0
            if i == 1:
                pwm_left = pwm
            if i == 3:
                pwm_right = pwm
        cmdStr = "$PWM=" +  str(pwm_left) + "," + str(pwm_right) + "*\n"
        textPrint.printScreen(screen, cmdStr)
        textPrint.unindent()
        if sendFlag:
            sock.sendto(cmdStr, (HOST, PORT))

        # buttons = joystick.get_numbuttons()
        # textPrint.printScreen(screen, "Number of buttons: {}".format(buttons) )
        # textPrint.indent()

        # for i in range( buttons ):
        #     button = joystick.get_button( i )
        #     textPrint.printScreen(screen, "Button {:>2} value: {}".format(i,button) )
        # textPrint.unindent()

        # # Hat switch. All or nothing for direction, not like joysticks.
        # # Value comes back in an array.
        # hats = joystick.get_numhats()
        # textPrint.printScreen(screen, "Number of hats: {}".format(hats) )
        # textPrint.indent()

        # for i in range( hats ):
        #     hat = joystick.get_hat( i )
        #     textPrint.printScreen(screen, "Hat {} value: {}".format(i, str(hat)) )

        textPrint.unindent()
        textPrint.unindent()


    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick(10)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
