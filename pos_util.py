""" Utility functions and classes dealing with position drawing """
from threading import Timer
import numpy as np
import cv2 as cv

class PosDrawer(object):
    """ Class to draw the marker of the current position on the waveform canvas. """

    def __init__(self, fr, fr_per_samp, h):
        """ 
        :param fr: framerate of the wav data
        :param fr_per_samp: frames per sample when drawing
        :param h: height of the canvas 
        """
        self.h = h
        self.draw_intvl = 5*float(fr_per_samp)/fr

        self._is_running = False
        self._pos_thread = None

        self._pos = None
        self.prev_y = None

    def set_pos(self, x):
        """
        Give the class a position to start drawing from

        :param x: x coordinate on the canvas of the click
        """
        self._pos = x

    def set_img(self, img):
        """
        Give the class a canvas to draw on. This is needed not just on initialization
        because display.py draws the starting position of the playback.

        TODO: Refactor so that all drawing (playback) is done from this class

        :param img: the numpy array to draw on
        """
        self.img = img

    def _run(self):
        """
        Increments the tracked position and draws the markers for that position

        Private function that is the target for the Timer thread.
        Called every self.draw_intvl seconds.
        """
        self._is_running = False
        self.start()
        self._pos += 1
        self.draw(self.img)

    def start(self):
        """
        Start drawing the playback marker. Called externally when the initial
        click is registered and internally on every call of self._run
        """
        if not self._is_running:
            self._pos_thread = Timer(self.draw_intvl, self._run)
            self._pos_thread.start()
            self._is_running = True

    def _erase_last_line(self, img):
        """
        Erase the last position marker drawn on the canvas. Not only does a line
        the height of the canvas need to be drawn in white, but the information
        stored about the amplitude of the waveform at that position is used so recolor
        it black.

        :param img: the canvas to erase the marker from
        """
        if not self.prev_y is None:
            prev_x = self._pos-1
            cv.line(img, (prev_x, 0), (prev_x, self.h), (255, 255, 255), 1)

            y1, y2 = self.prev_y
            cv.line(img, (prev_x, y1), (prev_x, y2), (0, 0, 0), 1)

    def draw(self, img):
        """
        Draw the marker for the current position on the canvas.

        :param pos: the canvas to draw the marker on
        """
        self._erase_last_line(self.img)

        idxs = np.argwhere(img[:, self._pos] == 0)
        self.prev_y = (idxs.min(), idxs.max())

        cv.line(img, (self._pos, 0), (self._pos, self.h), (0, 0, 0), 1)

    def stop(self, img):
        """
        Indicates playback has stopped. Erase the last marker drawn,
        stop the timer thread, and reset the position.

        :param img: the canvas to reset
        """
        self._erase_last_line(self.img)

        self._pos_thread.cancel()
        self._is_running = False

        self._pos = None
        self.prev_y = None
