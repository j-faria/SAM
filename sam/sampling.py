import pandas as pd
import matplotlib.pyplot as plt 

def read_RV_file(filename):
	data = pd.read_csv(filename, sep='\s+', comment='#', usecols=[0,1,2])
	try:
		data = data[data.time != '----']
	except (AttributeError, TypeError):
		pass
	try:
		data = data[data.jdb != '---']
	except (AttributeError, TypeError):
		pass

	t,y,e = data.astype(float).values.T
	return t,y,e


def has_extras(filename):
	num_columns = pd.read_csv(filename, sep='\s+', comment='#', nrows=1).shape[1]
	# file seems to have extras, besides time,RV,Rverr
	return num_columns > 3


def read_extras(filename):
	pass

class TimeSampling(object):
	def __init__(self, nobs=30, duration=None,
		         time=None, vrad=None, evrad=None):
		
		self.nobs = nobs
		self.duration = duration
		self.time, self.vrad, self.evrad = time, vrad, evrad

	def get_times(self):
		return self.time

	@classmethod
	def from_file(cls, filename):
		# try reading the file
		t,y,e = read_RV_file(filename)
		if has_extras(filename):
			pass
			# extras = read_extras(filename)

		nobs = t.size
		duration = t.ptp()

		return cls(nobs=nobs, duration=duration,
			       time=t, vrad=y, evrad=e)


	@property
	def gaps(self):
		""" A very rough estimation of the percentage of gaps """
		pass

	def plot(self):
		# if self.vrad is None
		fig = plt.figure(figsize=(8,3))
		ax1 = fig.add_subplot(211)
		ax1.vlines(self.time, ymin=0, ymax=1)
		ax2 = fig.add_subplot(212)
		ax2.plot(self.time, self.time.cumsum())
		for ax in (ax1, ax2):
			ax.set_yticks([])
		ax2.set_xlabel('Time [days]')
		fig.tight_layout()