from spppdd.spppdd import SPPPDD
import time


def spppdd_performance():
    s = SPPPDD()
    N = 128
    while True:
        start_time = time.time()
        for i in range(N):
            b = bytes(chr(i), 'ASCII')
            s.write_screen_raw(b * 153600)
        end_time = time.time()
        used_time = end_time - start_time
        print('Wrote {} frames in {} seconds, {} FPS'.format(N, used_time, N / used_time))

if __name__ == '__main__':
    spppdd_performance()
