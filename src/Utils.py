import numpy as np

class ProcessContext:

	def __init__(self, Fs : int, bpm : int, midi_resolution : int, concert_pitch : float = 440):
		self.Fs 				= Fs
		self.bpm 				= bpm
		self.midi_resolution 	= midi_resolution
		self.concert_pitch 		= concert_pitch