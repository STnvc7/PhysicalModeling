import numpy as np
import mido
from scipy.signal import butter, lfilter

class ProcessInfo:

	def __init__(self, Fs : int, bpm : int, midi_resolution : int, concert_pitch : float = 440):
		self.Fs 				= Fs
		self.bpm 				= bpm
		self.midi_resolution 	= midi_resolution
		self.concert_pitch 		= concert_pitch

def ticks_to_time(ticks, bpm, midi_resolution):

	return (60 / (bpm * midi_resolution)) * ticks

def ticks_to_sample(ticks, Fs, bpm, midi_resolution):

	return int((60 / (bpm * midi_resolution)) * ticks * Fs)

def number_to_frequency(midi_number, concert_pitch):

    return (concert_pitch / 32) * (2 ** ((midi_number - 9) / 12))


def butter_lowpass_filter(data, cutoff_freq: float, Fs: int, order: int = 4):
    nyquist = 0.5 * Fs
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = lfilter(b, a, data, axis=0)

    return filtered_data


def process_midi(proceess_info, midi_path : str):
    
    mid = mido.MidiFile(midi_path)
    track = mid.tracks[0]

    meta_msg = [m for m in track if m.is_meta == True]
    msg = [m for m in track if m.is_meta == False]
    
    ticks_per_beat = mid.ticks_per_beat
    clocks_per_click = proceess_info.midi_resolution
    k = clocks_per_click / ticks_per_beat
    current_time = 0
    notes = []

    for m in msg:
        if m.type == 'note_on':
            current_time += m.time
            note = {"onset" : int(current_time * k), "pitch" : m.note, "offset" : None, "velocity" : m.velocity, "string" : m.channel}
            notes.append(note)

        if m.type == 'note_off':
            current_time += m.time
            for note in notes[::-1]:
                if note['pitch'] == m.note and note['string'] == m.channel:
                    note['offset'] = int(current_time * k)
                    break
    return notes