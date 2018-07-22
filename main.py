import sys
import threading

import numpy as np
import sounddevice as sd

import cv2 as cv
import tkinter as tk
from tkinter import filedialog as fd

from tk_util import *
from wav_util import *
from pos_util import *

def open_wav():
    """ Prompt the user to select a wav file, open, and display the waveform. """
    path = fd.askopenfilename(
        initialdir='/users/samlerner/documents/samples',
        title='Select a WAV File', filetypes=[('WAV files', '*.wav')])
    
    global wav, fr
    wav, fr = get_wav_data(path)

    global w, h
    clear_img()
    draw_wav(wav[:,0], img, fr)
    set_img(img)

def draw_wav(wav, img, fr, s=0., e=3.5):
    """
    Draw an array of wav data onto a numpy array. Given a width per sample, an offset, and a padding,
    the number of frames per sample (fr_per_samp) can be calculated as:

        number_of_frames / number_of_samples

    where number_of_frames is the time_interval * frame_rate, or the number of frames to be displayed
    and number_of_samples is the width / (padding + sample_width), or the number of samples that can be fit on the canvas

    The mean of all fr_per_samp is then used to compute the height for that sample.

    :param wav: wav data (np.ndarray)
    :param img: canvas image (np.ndarray)
    :param s: first time (seconds) of the clip to display
    :param e: last time (seconds) of the clip to display
    """
    h, w = img.shape # dimensions of the canvas
    padding = 2 # number of pixels between samples
    offset = padding # initial offset for drawing
    w_per_samp = 3 # number of pixels per sample
    num_samp = w // (padding + w_per_samp) # number of samples that can fit on the canvas

    global max_amp, fr_per_samp
    max_amp = np.max(wav) # maximum amplitude of the data
    fr_per_samp = int((e - s)*fr / num_samp) # number of frames per sample

    for i in range(num_samp+1):
        samp = np.mean(np.abs(wav[i * fr_per_samp : (i+1) * fr_per_samp]))

        x = i*(padding + w_per_samp) + offset
        y1 = h//2 + int(h * samp/max_amp)
        y2 = h//2 - int(h * samp/max_amp)

        cv.line(img, (x, h//2), (x, y1), (0, 0, 0), w_per_samp)
        cv.line(img, (x, h//2), (x, y2), (0, 0, 0), w_per_samp)

def set_img(arr):
    """ 
    Set the image of the tkinter Canvas to the given numpy array

    :param arr: the numpy array to display
    """
    global tkImg, canvasImg, canvas
    tkImg = tk_img(arr)
    canvasImg = tk_imshow(canvas, tkImg)

def clear_img():
    """ Reset the canvas image to its original state (all white). """
    global img, h, w
    img = np.ones((h, w), np.uint8)*255

def play(event):
    """
    Play the audio from a given starting point when the window is clicked.

    :param event: the tkinter event
    """
    x, y = event.x, event.y

    global wav, fr
    global playing, pos_drawer
    global img
    global w, h
    global prev_x, prev_y

    # if we are currently playing, then erase the line drawn from the
    # previous x position.
    #
    # that will produce an ugly white line in the waveform, so the information
    # about the height of the waveform at the previous position is stored so that
    # that region can be redrawn as black. 
    if not prev_x is None:
        cv.line(img, (prev_x, 0), (prev_x, h), (255, 255, 255), 2)

        y1, y2 = prev_y
        cv.line(img, (prev_x, y1), (prev_x, y2), (0, 0, 0), 2)

        playing = False
        sd.stop() # stop playing if we are about to play from a different position
        pos_drawer.stop(img)

    # use the x-coordinate of the event as the point to start playing from
    start = int(len(wav) * x/w)
    from_x = wav[start:]

    playing = True
    sd.play(from_x, fr)

    pos_drawer.set_pos(x)
    pos_drawer.set_img(img)
    pos_drawer.start()

    prev_x = x

    # get the indeces of the column @ x that are black and store the
    # min and max so we can redraw the waveform at this position
    idxs = np.argwhere(img[:, x] == 0)
    prev_y = (idxs.min(), idxs.max())

    # draw the line showing where we're playing from
    cv.line(img, (x, 0), (x, h), (0, 0, 0), 2)
    set_img(img)

# Get the filename and load the waveform (along with the frame rate)
fname = sys.argv[1]
wav, fr = get_wav_data(fname)

# Global variables we will need everywhere
playing = False

max_amp = 0
fr_per_samp = 0

prev_x = None
prev_y = (None, None)

w, h = 850, 275
img = np.ones((h, w), np.uint8)*255

# Create the waveform display on the canvas and imshow it
draw_wav(wav[:,0], img, fr)
pos_drawer = PosDrawer(fr, fr_per_samp, h)

window = tk.Tk()

canvas = tk.Canvas(window, width=w, height=h)
canvas.bind('<Button-1>', play)
canvas.pack()

# tkImg, canvasImg, and canvas all need to be globally accessed everywhere.
# otherwise tkinter will flip out.
tkImg = tk_img(img)
canvasImg = tk_imshow(canvas, tkImg)

btn = tk.Button(window, text='Open File', command=open_wav)
btn.pack(side='bottom', fill='both', expand='yes', padx='10', pady='10')

window.mainloop()
