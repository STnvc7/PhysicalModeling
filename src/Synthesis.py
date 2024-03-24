import numpy as np
from scipy.io.wavfile import write

from DSP import KarplusStrong
import utils
from utils import ProcessInfo, process_midi

def get_model(proceess_info, model_type : str):

    if model_type == "KarplusStrong":
        model = KarplusStrong(process_info)

    return model

def synthesis(proceess_info, notes, model_type="KarplusStrong"):
    """
    辞書型のリストから合成
    """
    model = get_model(process_info, model_type)

    length = utils.ticks_to_sample(max([note['offset'] for note in notes]), process_info.Fs, process_info.bpm, process_info.midi_resolution)
    buffer = np.zeros(length)

    for note in notes:
        pitch = note['pitch']
        onset = note['onset']
        offset = note['offset']
        duration = offset - onset
        velocity = note['velocity']
        
        sample = model.pluck_string(pitch, velocity, duration)

        onset = utils.ticks_to_sample(onset, process_info.Fs, process_info.bpm, process_info.midi_resolution)
        duration = utils.ticks_to_sample(duration, process_info.Fs, process_info.bpm, process_info.midi_resolution)
        buffer[onset : onset+duration] = sample

    return buffer


if __name__ == "__main__":

    process_info = ProcessInfo(Fs=44010, bpm=100, midi_resolution=24, concert_pitch=440)
    p = "./bin/Stairway_to_heaven_90.mid" 
    notes=process_midi(process_info, p)
    audio = synthesis(process_info, notes) * np.iinfo(np.int16).max
    write("./test.wav", process_info.Fs, audio.astype(np.int16))