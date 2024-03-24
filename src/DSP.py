import numpy as np
from scipy.io.wavfile import write

import utils

class KarplusStrong:
	def __init__(self, process_info, buffer_size : int = 44010, feedback : float =0.5):
		
		self.Fs 				= process_info.Fs
		self.midi_resolution 	= process_info.midi_resolution
		self.bpm 				= process_info.bpm
		self.concert_pitch		= process_info.concert_pitch

		self.buffer_size = buffer_size
		self.feedback = feedback

		self.pluck_time = int(0.002 * self.Fs) #20ms

		self.delay_line = DelayLine(buffer_size)

	def pluck_string(self, midi_number : int, velocity : int, duration : int):

		F0 = utils.number_to_frequency(midi_number, self.concert_pitch)
		delay_time_sample = int(self.Fs / F0 - 0.5)
		length = utils.ticks_to_sample(duration, self.Fs, self.bpm, self.midi_resolution)

		input_buffer = np.zeros(length)
		output_buffer = np.zeros(length)

		factor = np.log10(velocity / 64) + 1
		input_buffer[0:self.pluck_time] = (np.random.rand(self.pluck_time) - 0.6) * factor
		input_buffer = utils.butter_lowpass_filter(input_buffer, 5000, self.Fs)


		for i, sample in enumerate(input_buffer):
			y_n_p   = self.delay_line.get(delay_time_sample)
			y_n_p_1 = self.delay_line.get(delay_time_sample+1)
			output_sample = np.tanh(sample + self.feedback * y_n_p + self.feedback * y_n_p_1)
			self.delay_line.push(output_sample)
			output_buffer[i] = output_sample

		return output_buffer

class DelayLine:
	def __init__(self, length):
		self.length = length
		self.buffer = np.zeros(length)
		self.index = 0

	def get_length(self):

		return self.length

	def clear(self):

		self.buffer = np.zeros(self.length) 
		return

	def push(self, sample):
		
		self.buffer[self.index] = sample

		if self.index == 0:
			self.index = self.length - 1
		else:
			self.index = self.index - 1;

		return

	def get(self, delayed_index):

		idx = (self.index + 1 + delayed_index) % self.length
		sample = self.buffer[idx]
		return sample

if __name__ == "__main__":

	from utils import ProcessInfo
	process_info = ProcessInfo(Fs=44010, bpm=100, midi_resolution=24, concert_pitch=440)
	KS = KarplusStrong(process_info)
	out = KS.pluck_string(60, 64, 48)
	out = out * np.iinfo(np.int16).max
	write("./C3.wav", 44010, out.astype(np.int16))