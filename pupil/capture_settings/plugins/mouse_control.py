"""
Stream Pupil gaze coordinate data using zmq to control a mouse with your eye.
Please note that marker tracking must be enabled, and in this example we have named the surface "screen."
You can name the surface what you like in Pupil capture and then write the name of the surface you'd like to use on line 17.
"""

# specify the name of the surface you want to use
surface_name = "screen"

## install dependencies
# pip3 install zmq msgpack pyuserinput

import zmq
from msgpack import loads
import subprocess as sp
from platform import system

if system() != "Sierra":
    from pymouse import PyMouse

    m = PyMouse()
    m.move(0, 0)  # hack to init PyMouse -- still needed


def move_mouse(x, y, click=False):
    if system() == "Sierra":
        sp.Popen(
            [
                "./mac_os_helpers/mouse",
                "-x",
                str(x),
                "-y",
                str(y),
                "-click",
                str(int(click)),
            ]
        )
    else:
        m.move(x, y)


def get_screen_size():
    if system() == "Sierra":
        screen_size = (
            sp.check_output(["./mac_os_helpers/get_screen_size"]).decode().split(",")
        )
        return float(screen_size[0]), float(screen_size[1])
    else:
        return m.screen_size()

# print(get_screen_size())

context = zmq.Context()
# open a req port to talk to pupil
addr = "127.0.0.1"  # remote ip or localhost
req_port = "50020"  # same as in the pupil remote gui
req = context.socket(zmq.REQ)
req.connect("tcp://{}:{}".format(addr, req_port))
# ask for the sub port
req.send_string("SUB_PORT")
sub_port = req.recv_string()

# open a sub port to listen to pupil
sub = context.socket(zmq.SUB)
sub.connect("tcp://{}:{}".format(addr, sub_port))
sub.setsockopt_string(zmq.SUBSCRIBE, f"surfaces.{surface_name}")

smooth_x, smooth_y = 0.5, 0.5

# screen size
x_dim, y_dim = get_screen_size()
print("x_dim: {}, y_dim: {}".format(x_dim, y_dim))

while True:
    topic, msg = sub.recv_multipart()
    gaze_position = loads(msg, encoding="utf-8")
    if gaze_position["name"] == surface_name:
        gaze_on_screen = gaze_position["gaze_on_surfaces"]
        if len(gaze_on_screen) > 0:

            # there may be multiple gaze positions per frame, so you could average them
            # raw_x = sum([i['norm_pos'][0] for i in gaze_on_screen])/len(gaze_on_screen)
            # raw_y = sum([i['norm_pos'][1] for i in gaze_on_screen])/len(gaze_on_screen)

            # or just use the most recent gaze position on the surface
            raw_x, raw_y = gaze_on_screen[-1]["norm_pos"]

            # smoothing out the gaze so the mouse has smoother movement
            smooth_x += 0.35 * (raw_x - smooth_x)
            smooth_y += 0.35 * (raw_y - smooth_y)
            x = smooth_x
            y = smooth_y

            y = 1 - y  # inverting y so it shows up correctly on screen
            x *= int(x_dim)
            y *= int(y_dim)
            # PyMouse or MacOS bugfix - can not go to extreme corners because of hot corners?
            x = min(x_dim - 10, max(10, x))
            y = min(y_dim - 10, max(10, y))

            # print "%s,%s\n" %(x,y)
            move_mouse(int(x), int(y))
