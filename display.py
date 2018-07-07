import sys
import threading

from numpy import fromstring
from numpy import iinfo, int16
import numpy as np

import sounddevice as sd
from scipy.io.wavfile import write
import wave

import cv2 as cv
import tkinter as tk

'''
Clip an array of wav data from s1 to s2 seconds

a - The array of sound values
s1 - the start (in seconds)
s2 - the end (in seconds)
'''
def zoom(a, s1, s2, fr):
    start_i = int(s1 * fr)
    end_i = int(s2 * fr)
    return a[start_i:end_i]

'''
Amplify the volume of an array of wav data my a multiplier

m - multiplier of amplitude
'''
def change_volume(a, m):
    assert a.ndim == 2
    for i, row in enumerate(a):
        for j, val in enumerate(row):
            a[i, j] = min(val * m, iinfo(a.dtype).max)
    return a

'''
Get an array of wav data from a given .wav file.
Return the frame rate also.

fname - path of the .wav file
'''
def get_wav_data(fname):
    f = wave.open(fname, 'r')

    sound_info = f.readframes(-1)
    sound_info = fromstring(sound_info, np.int16)
    sound_info = sound_info.reshape(len(sound_info)//2, 2)
    frrate = f.getframerate()

    f.close()
    return sound_info, frrate

from tkinter import filedialog as fd
def open_wav():
    path = fd.askopenfilename(
        initialdir='/users/samlerner/documents/samples',
        title='Select a WAV File', filetypes=[('WAV files', '*.wav')])
    
    global wav, fr
    wav, fr = get_wav_data(path)

    global w, h
    clear_img()
    draw_wav(wav[:,0], img, fr)
    set_img(img)

'''
Draw an array of wav data onto a numpy array

wav - wav data (np.ndarray)
img - canvas image (np.ndarray)
s - first time of the clip to display
e - last time of the clip to display
'''
def draw_wav(wav, img, fr, s=0., e=3.5):
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

    #print(fr, fr_per_samp, num_samp)
    #print(i*fr_per_samp)

'''
Update the numpy array being shown in the tkinter window
'''
def set_img(arr):
    global tkImg, canvasImg, canvas
    tkImg = tk_img(arr)
    canvasImg = tk_imshow(canvas, tkImg)

def clear_img():
    global img, h, w
    img = np.ones((h, w), np.uint8)*255

'''
Play the audio from a given starting point when the window is clicked

event - the tkinter event
'''
def play(event):
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

w, h = 1000, 300
img = np.ones((h, w), np.uint8)*255

# Create the waveform display on the canvas and imshow it
draw_wav(wav[:,0], img, fr)

from pos_util import PosDrawer
pos_drawer = PosDrawer(fr, fr_per_samp, h)

window = tk.Tk()

canvas = tk.Canvas(window, width=w, height=h)
canvas.bind('<Button-1>', play)
canvas.pack()

from tk_util import *

# tkImg, canvasImg, and canvas all need to be globally accessed everywhere.
# otherwise tkinter will flip out.
tkImg = tk_img(img)
canvasImg = tk_imshow(canvas, tkImg)

btn = tk.Button(window, text='Open File', command=open_wav)
btn.pack(side='bottom', fill='both', expand='yes', padx='10', pady='10')

window.mainloop()
