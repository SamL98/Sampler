""" Utility functions for dealing with tkinter. Mainly just wrappers. """
import tkinter as tk
from PIL import Image, ImageTk

def tk_img(arr):
    """
    Wrap a numpy array in a PhotoImage object from the PIL.ImageTk module.

    :param arr: the array to wrap
    """
    return ImageTk.PhotoImage(image=Image.fromarray(arr))

def tk_imshow(canvas, img):
    """
    Show the given PhotoImage on the given tkinter Canvas.

    :param canvas: the tk canvas to display on
    :param img: the tk image to display
    """
    return canvas.create_image(0, 0, image=img, anchor=tk.NW)