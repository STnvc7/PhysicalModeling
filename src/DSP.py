import numpy as np
from scipy.io.wavfile import write
from scipy.signal import butter, lfilter

class KarplusStrong:
	def __init__(self, Fs : int, buffer_size : int = 44010, feedback : float =0.5,
				 midi_resolution : int = 24, bpm : int = 100, A_Hz : float = 440):
		
		self.Fs = Fs
		self.buffer_size = buffer_size
		self.feedback = feedback
		self.midi_resolution = midi_resolution
		self.bpm = bpm
		self.A_Hz = A_Hz

		self.pluck_time = int(0.002 * Fs) #20ms

		self.delay_line = DelayLine(buffer_size)

	def number_to_frequency(self, midi_number : int):
	    return (self.A_Hz / 32) * (2 ** ((midi_number - 9) / 12))

	def ticks_to_time(self, ticks : int):
		return (60 / (self.bpm * self.midi_resolution)) * ticks

	def butter_lowpass_filter(self, data, cutoff_freq: float, Fs: int, order: int = 4):
	    nyquist = 0.5 * Fs
	    normal_cutoff = cutoff_freq / nyquist
	    b, a = butter(order, normal_cutoff, btype='low', analog=False)
	    filtered_data = lfilter(b, a, data, axis=0)

	    return filtered_data

	def pluck_string(self, midi_number : int, velocity : int, duration : int):

		F0 = self.number_to_frequency(midi_number)
		delay_time_sample = int(self.Fs / F0 - 0.5)
		length = int(self.ticks_to_time(duration) * self.Fs)

		input_buffer = np.zeros(length)
		factor = np.log10(velocity / 64) + 1
		input_buffer[0:self.pluck_time] = (np.random.rand(self.pluck_time) - 0.6) * factor
		input_buffer = self.butter_lowpass_filter(input_buffer, 5000, self.Fs)
		output_buffer = []

		for i, sample in enumerate(input_buffer):
			y_n_p   = self.delay_line.get(delay_time_sample)
			y_n_p_1 = self.delay_line.get(delay_time_sample+1)
			output_sample = np.tanh(sample + self.feedback * y_n_p + self.feedback * y_n_p_1)
			self.delay_line.push(output_sample)
			output_buffer.append(output_sample)

		return np.array(output_buffer)

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
	KS = KarplusStrong(44010)
	out = KS.pluck_string(60, 64, 48)
	out = out * np.iinfo(np.int16).max
	write("./C3.wav", 44010, out.astype(np.int16))