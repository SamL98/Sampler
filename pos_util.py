from threading import Timer
import numpy as np
import cv2 as cv

class PosDrawer(object):
    def __init__(self, fr, fr_per_samp, h):
        self.h = h
        self.draw_intvl = 5*float(fr_per_samp)/fr

        self._is_running = False
        self._pos_thread = None

        self._pos = None
        self.prev_y = None

    def set_pos(self, x):
        self._pos = x

    def set_img(self, img):
        self.img = img

    def _run(self):
        self._is_running = False
        self.start()
        self._pos += 1
        self.draw(self.img)

    def start(self):
        if not self._is_running:
            self._pos_thread = Timer(self.draw_intvl, self._run)
            self._pos_thread.start()
            self._is_running = True

    def _erase_last_line(self, img):
        if not self.prev_y is None:
            prev_x = self._pos-1
            cv.line(img, (prev_x, 0), (prev_x, self.h), (255, 255, 255), 1)

            y1, y2 = self.prev_y
            cv.line(img, (prev_x, y1), (prev_x, y2), (0, 0, 0), 1)

    def draw(self, img):
        self._erase_last_line(self.img)

        idxs = np.argwhere(img[:, self._pos] == 0)
        self.prev_y = (idxs.min(), idxs.max())

        cv.line(img, (self._pos, 0), (self._pos, self.h), (0, 0, 0), 1)

    def stop(self, img):
        self._erase_last_line(self.img)

        self._pos_thread.cancel()
        self._is_running = False

        self._pos = None
        self.prev_y = None
