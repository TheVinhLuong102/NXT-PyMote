#!python

from jaraco.nxt import *
from jaraco.nxt.messages import *

import time
import sdl2
import math

sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
joystick = sdl2.SDL_JoystickOpen(0)

# open the connection. Get this string from preferences>bluetooth>NXT>edit serial ports
conn = Connection('/dev/tty.Addy-DevB')  # antons NXT


def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)


while True:
    sdl2.SDL_PumpEvents()

    # read joystick input and normalise it to a range of -100 to 100
    joy_x = (sdl2.SDL_JoystickGetAxis(joystick, 0) - 17268) / 172.68
    joy_y = (sdl2.SDL_JoystickGetAxis(joystick, 1) - 17268) / 172.68

    # use shoulder buttons on the game pad to make the omnibot rotate around it's axis.
    turnpower = 0
    if sdl2.SDL_JoystickGetButton(joystick, 5):turnpower = 75
    if sdl2.SDL_JoystickGetButton(joystick, 4):turnpower = -75

    # convert joystick x and y to a direction and power (deviation from the centre)
    joy_direction = math.atan2(joy_y, joy_x)  # in radians
    joy_power = (joy_x ** 2 + joy_y ** 2) ** 0.5  # pythagoras

    # building a list of three motor commands to send over
    cmds = []
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

    map(conn.send, cmds)

    # wait a bit before sending more commands. If we don't the BT buffer overflows.
    time.sleep(0.05)

    # end the fun if button 1 is pressed.
    if sdl2.SDL_JoystickGetButton(joystick, 0) : break

# clean up
conn.close()
