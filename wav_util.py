import numpy as np
import wave

def zoom(a, s1, s2, fr):
    """
    Clip an array of wav data from s1 to s2 seconds

    :param a: The array of sound values
    :param s1: the start (in seconds)
    :param s2: the end (in seconds)
    """
    start_i = int(s1 * fr)
    end_i = int(s2 * fr)
    return a[start_i:end_i]

def change_volume(a, m):
    """
    Amplify the volume of an array of wav data my a multiplier

    :param m: multiplier of amplitude
    """
    assert a.ndim == 2
    for i, row in enumerate(a):
        for j, val in enumerate(row):
            a[i, j] = min(val * m, np.iinfo(a.dtype).max)
    return a

def get_wav_data(fname):
    """
    Get an array of wav data from a given .wav file.
    Return the frame rate also.

    :param fname: path of the .wav file
    """
    with wave.open(fname, 'r') as f:
        arr = f.readframes(-1)
        arr = np.fromstring(arr, np.int16)
        arr = arr.reshape(len(arr)//2, 2)
        frrate = f.getframerate()

    return arr, frrate