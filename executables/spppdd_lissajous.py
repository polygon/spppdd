import numpy as np
from spppdd.spppdd import SPPPDD
import time
import colorsys


def spppdd_lissajous():
    s = SPPPDD()
    start_time = time.time()
    while True:
        t = time.time() - start_time
        a = 0.5 * np.sin(0.013*t) + 2
        b = 0.8 * np.cos(0.018*t) + 3.5
        h = 0.5 + np.sin(0.2*t) / 2.
        s.write_screen_numpy(draw_lissajous(a, b, h))


def draw_lissajous(a, b, h):
    t = np.arange(0, 16*np.pi, np.pi/1024)
    x = (159 * np.sin(a*t) + 159).astype(np.uint)
    y = (119 * np.cos(b*t) + 119).astype(np.uint)
    picture = np.zeros((320, 240, 3))
    picture[x, y, :] = np.array(colorsys.hsv_to_rgb(h, 1.0, 1.0))
    return picture


if __name__ == '__main__':
    spppdd_lissajous()