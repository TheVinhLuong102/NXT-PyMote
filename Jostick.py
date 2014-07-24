import sdl2

sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
joystick = sdl2.SDL_JoystickOpen(0)
joystick2 = sdl2.SDL_JoystickOpen(1)
player = {'gamepad': joystick2,
          'stick_range': 65536,  # max stick position - min stick position
          'stick_center': 0,
          'left_shoulder_btn':8,
           'right_shoulder_btn':9}

while True:
    sdl2.SDL_PumpEvents()
    btns = {}
    for i in range(15):
        btns[i] = sdl2.SDL_JoystickGetButton(joystick2, i)

    joy_x = (sdl2.SDL_JoystickGetAxis(player['gamepad'], 0) - player['stick_center']) * 200 / player['stick_range']
    print(joy_x, (sdl2.SDL_JoystickGetAxis(joystick2, 0) - 0) * 200 / 65000,
          sdl2.SDL_JoystickGetAxis(joystick2, 1),
          btns)
    if sdl2.SDL_JoystickGetButton(player['gamepad'], player['left_shoulder_btn']) :break

