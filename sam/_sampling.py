# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

# def read_RV_file(filename):
#     data = pd.read_csv(filename, sep='\s+', comment='#', usecols=[0,1,2])
#     try:
#         data = data[data.time != '----']
#     except (AttributeError, TypeError):
#         pass
#     try:
#         data = data[data.jdb != '---']
#     except (AttributeError, TypeError):
#         pass
#
#     t,y,e = data.astype(float).values.T
#     return t,y,e


def read_RV_file(filename):
    t,y,e = [],[],[]
    with open(filename) as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            split_line = line.split()
            if '--' in split_line[0]:
                continue

            try:
                t.append(float(split_line[0]))
                y.append(float(split_line[1]))
                e.append(float(split_line[2]))
            except ValueError:
                continue

            # print line.split()
    assert len(t) == len(y) == len(e), 'Different sizes!'
    return tuple(map(np.array, [t,y,e]))


def has_extras(filename):
    # num_columns = pd.read_csv(filename, sep='\s+', comment='#', nrows=1).shape[1]
    # file seems to have extras, besides time,RV,Rverr
    with open(filename) as f:
        for line in f.readlines():
            if line.startswith('#'):
                continue
            split_line = line.split()
            if '--' in split_line[0]:
                continue
            else:
                num_columns = len(split_line)

    return num_columns > 3


def read_extras(filename):
    pass

class TimeSampling(object):
    def __init__(self, times, nobs=30, duration=None):
        
        self.time = times

    @property
    def duration(self):
        return self.time.ptp()
    
    @property
    def nobs(self):
        return len(self.time)

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

        return cls(time=t, nobs=nobs, duration=duration)


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