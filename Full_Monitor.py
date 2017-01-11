# -*- coding: utf-8 -*-
"""
Created on Wed Oct  5 08:12:41 2016

@author: julchak
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from datetime import datetime, timedelta
import collections
import csv


TIME_WINDOW = 3     # minutes

class Anim():
    """
    This class provides a "live" plot of the contents of a log file in csv format. 
    The class structure makes it easy to separate the plot generation from the
        frequent updating of the plot.
    The code is based on a question at stackoverflow
        http://stackoverflow.com/questions/39858501/python-data-display-with-graph
    """
    def __init__(self):

        self.offset = 16.
        self.slope = -.2081

        self.num_cycles = 0

        self.axisbg = '#07000d'

        self.fig = plt.figure(figsize=(20,15), facecolor=self.axisbg)
        self.ax = self.fig.add_subplot(111, axisbg=self.axisbg)

        [self.ax.spines[wh].set_color("#5998ff") for wh in ['bottom', 'top', 'left', 'right']]

        self.hfmt = matplotlib.dates.DateFormatter('%m/%d/%Y\n%I:%M:%S %p')
        self.ax.xaxis.set_major_formatter(self.hfmt)
        self.fig.autofmt_xdate()

        #self.framenumber = plt.figtext(0.9, .9, "0",  color='w')
        self.ax.grid(True, color='w')
        plt.ylabel('Tension (lb)', color='w', fontsize=20)
        plt.title('Integrated Intelligece Monitor', color='w', fontsize=26)

        self.ax.tick_params(axis='y', colors='w')
        self.ax.tick_params(axis='x', colors='w')

        initialx = [self.stime("09/28/2016 17:34:28.967"), self.stime("09/28/2016 17:34:29.716")]
        initialy = [0, 0]

        self.line1, = self.ax.plot(matplotlib.dates.date2num(initialx), initialy, color="c", linewidth=2)
        self.line2, = self.ax.plot(matplotlib.dates.date2num(initialx), initialy, color="r", linewidth=2)
        self.line3, = self.ax.plot(matplotlib.dates.date2num(initialx), initialy, color="y", linewidth=2)

        plt.subplots_adjust(left=0.1, bottom=0.28, right=0.9, top=0.9, wspace=0, hspace=0)

        self.ax_temp =      plt.axes([0.1, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_time =      plt.axes([0.18, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_overdrive = plt.axes([0.24, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_cycles =    plt.axes([0.31, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_drum =      plt.axes([0.36, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_belt =      plt.axes([0.44, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_image =     plt.axes([0.6, -0.01, 0.3, 0.2], axisbg=self.axisbg)

        self.tx_temp = self.ax_temp.text(0,0, "Temp", color="w", transform=self.ax_temp.transAxes, bbox={"pad" : 10, "ec" : "w", "fc" : self.axisbg})
        self.tx_time = self.ax_time.text(0,0, "Time", color="w", transform=self.ax_time.transAxes, bbox={"pad" : 10, "ec" : "w", "fc" : self.axisbg})
        self.tx_overdrive = self.ax_overdrive.text(0,0, "Overdrive", color="w", transform=self.ax_overdrive.transAxes, bbox={"pad" : 10, "ec" : "w", "fc" : self.axisbg})
        self.tx_cycles = self.ax_cycles.text(0,0, "Cyles", color="w", transform=self.ax_cycles.transAxes, bbox={"pad" : 10, "ec" : "w", "fc" : self.axisbg})
        self.tx_drum = self.ax_drum.text(0,0, "Drum", color="w", transform=self.ax_drum.transAxes, bbox={"pad" : 10, "ec" : "w", "fc" : self.axisbg})
        self.tx_belt = self.ax_belt.text(0,0, "Belt", color="w", transform=self.ax_belt.transAxes, bbox={"pad" : 10, "ec" : "w", "fc" : self.axisbg})

        self.ax_image.imshow(mpimg.imread('logo.jpg'))
        self.ax_image.tick_params(axis='x',which='both',bottom='off', top='off',labelbottom='off')
        self.ax_image.tick_params(axis='y',which='both',left='off', right='off',labelleft='off')
        [self.ax_image.spines[wh].set_color("#5998ff") for wh in ['bottom', 'top', 'left', 'right']]

        self.timer = self.fig.canvas.new_timer(interval=250, callbacks=[(self.animate, [], {})])
        self.timer.start()
        plt.show()


    def plot(self, data, line):
        if data:
            last_dt = data[0][0]
            gap = timedelta(seconds=10)
            x = []
            y = []
            # Plot groups of data not more than 60 seconds apart
            for dt, ten in data:
                if dt <= last_dt + gap:
                    x.append(dt)
                    y.append(ten)
                else:
                    line.set_data(matplotlib.dates.date2num(x), y)
                    #ax.plot(, colour, linewidth=width)
                    x = [dt]
                    y = [ten]
                last_dt = dt
            line.set_data(matplotlib.dates.date2num(x), y)


    def animate(self):
        self.num_cycles +=1 #counting the number of frames
        # Read in the CSV file
        data = collections.defaultdict(list)
        fields = ["TimeStamp", "ReadCount", "Antenna", "Protocol", "RSSI", "EPC", "Temp", "Ten", "Powr", "Unpowr", "Inf"]
        temp = ""
        # the complete file is read in, which might be a problem once the file gets very large
        with open('SensorLogFiletest.csv') as f_input:
            csv_input = csv.DictReader(f_input, skipinitialspace=True, fieldnames=fields)
            header = next(csv_input)
            # Separate the rows based on the Antenna field
            for row in csv_input:
                try:
                    data[row['Antenna']].append([self.stime(row['TimeStamp']), self.rten(row['Ten']) ])
                    temp= row['Temp']
                except:
                    pass

        # Drop any data points more than 1.5 mins older than the last entry
        latest_dt = data[row['Antenna']][-1][0]     # Last entry
        not_before = latest_dt - timedelta(minutes=TIME_WINDOW)

        for antenna, entries in data.items():
            data[antenna] = [[dt, count] for dt, count in entries if dt >= not_before]

        self.plot(data['1'],  self.line2)     # Antenna 1
        self.plot(data['2'],  self.line1)     # Antenna 2
        self.plot(data['3'],  self.line3)     # Antenna 3

        #Filling the text boxes
        self.tx_temp.set_text(u"Temperature\n   {temp:.2f} °F".format(temp=self.deg2F(temp)))
        self.tx_time.set_text("   Time\n{}".format(datetime.now().strftime("%H:%M:%S")))
        self.tx_overdrive.set_text("Overdrive\n   ---------")
        #Todo: how do you calculate this?
        self.tx_cycles.set_text("Cyles\n {cyles}".format(cyles=self.num_cycles)) 
        self.tx_drum.set_text("Drum Speed\n {}".format('   -----------') )
        self.tx_belt.set_text("Belt Speed\n {sp:.2f} (ft/s)".format(sp=23.1234) )
        #Todo: setting the limits correctly, depending on the user's need
        self.ax.set_ylim([0,16])     
        self.ax.set_xlim([matplotlib.dates.date2num(not_before), matplotlib.dates.date2num(latest_dt)])
        #Update the canvas
        self.fig.canvas.draw()


    def deg2F(self,deg):
        return float(deg) * 9./5. + 32. 

    def stime(self, timestamp):
        return datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S.%f')

    def rten(self, ten):
        return int(float(ten) * self.slope + self.offset)


if __name__ == "__main__":
    Anim()