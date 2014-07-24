#!python

from jaraco.nxt import *
from jaraco.nxt.messages import *

import time
import sdl2
import math

# initialise joysticking
sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)

# create configs
AntoBot = {
           'tty': '/dev/tty.NXT-DevB',
           'gamepad_num': 0,
           'gamepad' : sdl2.SDL_JoystickOpen(0),
           'stick_range': 32768,  # max stick position - min stick position
           'stick_center': 17268,
           'left_shoulder_btn' : 4,
           'right_shoulder_btn' :5,
           'invert_y' : 1,
           'abort_btn' : 3
           }

AddyBot = {
           'tty': '/dev/tty.Addy-DevB',
           'gamepad_num': 1,
           'gamepad' : sdl2.SDL_JoystickOpen(1),  # sixaxis
           'stick_range': 65536,  # max stick position - min stick position
           'stick_center': 0,
           'left_shoulder_btn':8,
           'right_shoulder_btn':9,
           'invert_y' :-1,
           'abort_btn' : 12
           }

players = [AddyBot, AntoBot]

for player in players:
    player['conn'] = Connection(player['tty'])


# open the connection. Get this string from preferences>bluetooth>NXT>edit serial ports


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

running = 1
while running:
    sdl2.SDL_PumpEvents()

    for player in players:
        # read joystick input and normalise it to a range of -100 to 100
        joy_x = (sdl2.SDL_JoystickGetAxis(player['gamepad'], 0) - player['stick_center']) * 200 / player['stick_range']
        joy_y = (sdl2.SDL_JoystickGetAxis(player['gamepad'], 1) - player['stick_center']) * 200 / player['stick_range'] * player['invert_y']


        # use shoulder buttons on the game pad to make the omnibot rotate around it's axis.
        turnpower = 0
        if sdl2.SDL_JoystickGetButton(player['gamepad'], player['right_shoulder_btn']):turnpower = 75
        if sdl2.SDL_JoystickGetButton(player['gamepad'], player['left_shoulder_btn']):turnpower = -75

        # end the fun if button 1 is pressed.
        if sdl2.SDL_JoystickGetButton(player['gamepad'], player['abort_btn']) :
            print 'stopping'
            running = 0

        btns = {}
        for i in range(15):
            btns[i] = sdl2.SDL_JoystickGetButton(player['gamepad'], i)

        # print(joy_x, joy_y, turnpower, btns)


        # convert joystick x and y to a direction and power (deviation from the centre)
        joy_direction = math.atan2(joy_y, joy_x)  # in radians
        joy_power = (joy_x ** 2 + joy_y ** 2) ** 0.5  # pythagoras

        # building a list of three motor commands to send over
        cmds = []

        # deadzone
        if (joy_power < 10 and turnpower == 0):
            joy_power = 0
            for i in range(3):
                cmds.append(SetOutputState(
                                          i,
                                          motor_on=False,
                                          set_power=0
                                          )
                        )
            map(player['conn'].send, cmds)
        else :
            for i in range(3):
                # for each motor the angle has a different offset (0, 120 and 240 degrees)
                angle = i * 2 * 3.1415 / 3 + joy_direction

                # motor power calculation. A simple sin.
                motorpower = math.sin(angle) * joy_power + turnpower

                motorpower = round(clamp(motorpower, -100, 100))

                cmds.append(SetOutputState(
                                          i,
                                          motor_on=True,
                                          set_power=motorpower,
                                          run_state=RunState.running,
                                          use_regulation=True,
                                          regulation_mode=RegulationMode.motor_speed
                                          )
                        )
            map(player['conn'].send, cmds)



    # wait a bit before sending more commands. If we don't the BT buffer overflows.
    time.sleep(0.05)



# clean up
for player in players:
    # turn off all motors before disconnecting
    for i in range(3):
            cmds.append(SetOutputState(
                                          i,
                                          motor_on=False,
                                          set_power=0
                                          )
                        )
            map(player['conn'].send, cmds)

    player['conn'].close
