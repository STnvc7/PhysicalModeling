import numpy as np
from scipy.io.wavfile import write
import mido
import polars as pl
from DSP import KarplusStrong

def get_model(model_type : str):

    if model_type == "KarplusStrong":
        model = KarplusStrong()

    return model

def synthesis(notes, model_type="KarplusStrong"):
    """
    辞書型のリストから合成
    """
    model = get_model(model_type)
    for note in notes:
        pitch = note['pitch']
        onset = note['onset']
        duration = note['duration']
        velocity = note['velocity']
        
        sample = pluck_string(pitch, onset, duration, velocity)

def process_midi(message):
    pass

def pluck_string(pitch, velocity, duration):
    
    

if __name__ == "__main__":
    # path = ""
    # note = pl.read_csv()
    # synthesis()
    print("testtttt")