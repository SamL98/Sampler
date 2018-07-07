import tkinter as tk
from PIL import Image, ImageTk

def tk_img(arr):
    return ImageTk.PhotoImage(image=Image.fromarray(arr))

def tk_imshow(canvas, img):
    return canvas.create_image(0, 0, image=img, anchor=tk.NW)