#!/usr/bin/python
import socket
import numpy as np
import sys
import signal
import time
import threading
from threading import Thread
import curses
from curses import wrapper
from curses import ascii


"""
@brief Keyboard control for the QuickBot.

@description This program is used to drive the QuickBot via the keyboard

@author Rowland O'Flaherty (rowlandoflaherty.com)
@author Marty Kube marty@beavercreekconsulting.com
@date 2015-04-20

@note Works with 64-bit python

@version: 1.0
@copyright: Copyright (C) 2014, Georgia Tech Research Corporation see
the LICENSE file included with this software (see LINENSE file)
"""



# Constants
LEFT = 0
RIGHT = 1
FORWARD = 1
BACKWARD = -1
SEND_FLAG = True

# Get input arguments
LOCAL_IP = "192.168.1.168" # Computer IP address (change to correct value)
QB_IP = "192.168.1.160" # QuickBot IP address (change to correct value)
PORT = 5005
if len(sys.argv) > 2:
    print 'Invalid number of command line arguments.'
    print 'Usage:'
    print '>> consoleControl.py <robot-ip>'
    print 'Example:'
    print '>> consoleControl.py ', QB_IP
    sys.exit()

if len(sys.argv) == 2:
    QB_IP = sys.argv[1]

class QuickBot:
    # Parameters -- (LEFT, RIGHT)
    pwmMinVal = [35, 35]
    pwmMaxVal = [100, 100]

    # State -- (LEFT, RIGHT)
    pwm = [0.0, 0.0]
    pwmDelta = [2, 2]

    def __init__(self, socket):
        self.socket = socket
        # last command sent
        self.cmdStr = ''

    def send(self):
        self.socket.sendto(self.cmdStr, (QB_IP, PORT))

    def receive(self):
        return self.socket.recv(2048)

    def stop(self):
        self.pwm = [0, 0]

    def update(self):
        # Slow down
        slowDownRate = 2
        for side in range(0, 2):
            if self.pwm[side] > 0:
                self.accelerateByVal(-1*slowDownRate, side)
            elif self.pwm[side] < 0:
                self.accelerateByVal(slowDownRate, side)

    def accelerate(self, dir, side):
        self.accelerateByVal(dir*self.pwmDelta[side], side)

    def accelerateByVal(self, val, side):
        way = np.sign(val)
        if self.pwm[side] == 0:
            self.pwm[side] = way*self.pwmMinVal[side]
        elif (self.pwm[side] == self.pwmMinVal[side] and way < 0) or (
                self.pwm[side] == -1*self.pwmMinVal[side] and way > 0):
            self.pwm[side] = 0
        else:
            self.pwm[side] = self.pwm[side] + val

        if self.pwm[side] > 0:
            self.pwm[side] = min(self.pwm[side], self.pwmMaxVal[side])
        elif self.pwm[side] < 0:
            self.pwm[side] = max(self.pwm[side], -1*self.pwmMaxVal[side])

    def setPWM(self):
        self.cmdStr = "$PWM=" + str(QB.pwm[LEFT]) + "," + \
            str(QB.pwm[RIGHT]) + "*\n"
        self.send()

    def getIR(self):
        self.cmdStr = "$IRVAL?*\n"
        self.send()

    def getEncoderVal(self):
        self.cmdStr = "$ENVAL?*\n"
        self.send()

    def resetEncoder(self):
        self.cmdStr = "$RESET*\n"
        self.send()

    def healthCheck(self):
        self.cmdStr = "$CHECK*\n"
        self.send()

    def calibrate(self):
        self.pwm[LEFT] = 90
        self.pwm[RIGHT] = 80
        self.setPWM()

    def end(self):
        self.cmdStr = "$END*\n"
        self.send()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setblocking(False)
print 'Binding to %s %d' % (LOCAL_IP, PORT);
sock.bind((LOCAL_IP, PORT))
QB = QuickBot(sock)


class Console:
    """
    Class to interact with screen
    """
    TITLE_ROW = 0
    SENT_ROW = 1
    RECEIVE_ROW = 2
    PROMPT_ROW = 3

    def __init__(self):
        self.sentMsg = ''
        self.receivedMsg = ''
        self.promptMsg = ''
        self.screen = None

    def sent(self, msg = ''):
        self.sentMsg = msg
        self.paint()
            
    def received(self, msg):
        self.receivedMsg = msg
        self.paint()

    def prompt(self, msg = ' '):
        self.promptMsg = msg
        self.paint()

    def paint(self):
        if self.screen != None:
            
            self.screen.addstr(self.TITLE_ROW, 0, ' ' * curses.COLS, curses.A_REVERSE)
            self.screen.addstr( self.TITLE_ROW, 0, 'Quickbot Control', curses.A_REVERSE)
            
            self.screen.addstr(self.SENT_ROW, 0,    'Sent    : ')
            self.screen.addstr(self.sentMsg)

            self.screen.addstr(self.RECEIVE_ROW, 0, 'Received: ')
            self.screen.addstr(self.receivedMsg)

            self.screen.addstr(curses.LINES - 3, 0, ' ' * curses.COLS, curses.A_REVERSE)
            self.screen.addstr(curses.LINES - 3, 0, 'Forward/Backward: up/down arrow, Left/Right: left/righ arrow, Stop: space', curses.A_REVERSE)

            self.screen.addstr(curses.LINES - 2, 0, ' ' * curses.COLS, curses.A_REVERSE)
            self.screen.addstr(curses.LINES - 2, 0, 'Left Wheel: a/z, Right Wheel: s/x', curses.A_REVERSE)

            self.screen.move(curses.LINES - 1, 0)
            self.screen.addstr(' ' * (curses.COLS - 1), curses.A_REVERSE)
            self.screen.addstr(curses.LINES - 1, 0, 'Quit: q, Encoder: e, IR: r, Reset Encoder: t, Check Status: c', curses.A_REVERSE)

            self.screen.addstr(curses.LINES - 4, 0, '> ')
            self.screen.addstr(self.promptMsg)

            self.screen.refresh()

    def run(self, screen):
        
        self.screen = screen
        self.paint()

        while True:
            
            c = screen.getch()

            if curses.ascii.islower(c):
                self.prompt(chr(c))

            # End program
            if c == curses.ascii.ESC:
                break
            
            if c == ord('q'):
                break

            # Stop robot
            if c == curses.ascii.SP:
                QB.stop()
                QB.setPWM()
    
            # Move right wheel
            elif c == ord('s'):
                QB.accelerate(FORWARD, LEFT)
                QB.setPWM()

            elif c == ord('x'):
                QB.accelerate(BACKWARD, LEFT)
                QB.setPWM()

            # Move left wheel
            elif c == ord('a'):
                QB.accelerate(FORWARD, RIGHT)
                QB.setPWM()

            elif c == ord('z'):
                QB.accelerate(BACKWARD, RIGHT)
                QB.setPWM()

            # Move forward/backward
            elif c == curses.KEY_UP:
                QB.accelerate(FORWARD, LEFT)
                QB.accelerate(FORWARD, RIGHT)
                QB.setPWM()

            elif c == curses.KEY_DOWN:
                QB.accelerate(BACKWARD, LEFT)
                QB.accelerate(BACKWARD, RIGHT)
                QB.setPWM()

            # Turn left/right
            elif c == curses.KEY_RIGHT:
                QB.accelerate(BACKWARD, LEFT)
                QB.accelerate(FORWARD, RIGHT)
                QB.setPWM()

            elif c == curses.KEY_LEFT:
                QB.accelerate(FORWARD, LEFT)
                QB.accelerate(BACKWARD, RIGHT)
                QB.setPWM()

            # Encoder query
            elif c == ord('e'):
                QB.getEncoderVal()

            # Encoder reset
            elif c == ord('t'):
                QB.resetEncoder()

            # IR query
            elif c == ord('r'):
                QB.getIR()

            # Health Check
            elif c == ord('c'):
                QB.healthCheck()

            # Calibrate motor
            elif c == ord('m'):
                QB.calibrate()

            # Don't know this character
            else:
                self.prompt()

            # Update display for last command
            self.sent(QB.cmdStr)


console = Console()

def poll():
    count = 1
    while True:
        try:
            data = sock.recv(2048)
            console.received(data)
        except socket.error as mesg:
            pass
        time.sleep(0.1)


def main(screen):
    t = threading.Thread(target=poll)
    t.setDaemon(True)
    t.start()
    console.run(screen)


wrapper(main)
