# -*- coding: utf-8 -*-
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from datetime import datetime, timedelta
import collections
import csv
import os

TIME_WINDOW = 3     # minutes
DISTANCES = [40.4, 40.4, 103.1]

class Anim():
    """
    This class provides a "live" plot of the contents of a log file in csv format. 
    The class structure makes it easy to separate the plot generation from the
        frequent updating of the plot.
    The code is based on a question at stackoverflow
        http://stackoverflow.com/questions/39858501/python-data-display-with-graph
    """
    file = 'SensorLog.csv'

    def __init__(self):

        self.offset = -167.851
        self.slope = 1.5351
        self.last_time = datetime(2016, 1, 18, 10, 9, 19, 323815)

        self.num_cycles = 0

        self.axisbg = '#07000d'

        self.fig = plt.figure(figsize=(20,15), facecolor=self.axisbg)
        self.ax = self.fig.add_subplot(111, axisbg=self.axisbg)

        [self.ax.spines[wh].set_color("#5998ff") for wh in ['bottom', 'top', 'left', 'right']]
        self.fig.autofmt_xdate()

        self.ax.tick_params(axis='y', colors='w')
        self.ax.tick_params(axis='x', colors='w')

        plt.subplots_adjust(left=0.1, bottom=0.28, right=0.9, top=0.9, wspace=0, hspace=0)

        self.ax_temp =      plt.axes([0.1, 0.08, 0.2, 0.06],  axisbg=self.axisbg)
        self.ax_time =      plt.axes([0.19, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_belt =      plt.axes([0.26, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_cycles =    plt.axes([0.343, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_drum =      plt.axes([0.4, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_overdrive = plt.axes([0.485, 0.08, 0.2, 0.06], axisbg=self.axisbg)
        self.ax_image =     plt.axes([0.6, -0.01, 0.3, 0.2],  axisbg=self.axisbg)

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

        self.timer = self.fig.canvas.new_timer(interval=500, callbacks=[(self.animate, [], {})])
        self.timer.start()
        plt.show()

    def plot(self, data, color):
        if data:
            gap = timedelta(seconds=3)      # for discret graph
            xx0, xx1 = [], []
            yy0, yy1 = [], []

            last_dt = None
            for dt, ten in data:
                if last_dt and dt <= last_dt + gap:
                    xx0.append(last_dt)
                    xx1.append(dt)
                    yy0.append(last_ten)
                    yy1.append(ten)
                last_dt = dt
                last_ten = ten

            xxx = [xx0, xx1]
            yyy = [yy0, yy1]

            self.ax.plot(matplotlib.dates.date2num(xxx), yyy, linewidth=2, color=color)

    def animate(self):
        self.ax.clear()
        self.ax.grid(True, color='w')
        self.ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d/%Y\n%I:%M:%S %p'))
        self.ax.set_title('Integrated Intelligence Monitor', color='w', fontsize=26)
        self.ax.set_ylabel('Tension (lb)', color='w', fontsize=20)

        # Read in the CSV file
        data = collections.defaultdict(list)

        temp = 0
        antenna = 0
        start_timestamp = 0         # start of new antenna
        min_y, max_y = 100000, 0
        first_time = None           # start of graph
        sp = 0
        for line in self.read_last_n_line():
            try:
                row = line.split(',')
                timestamp = self.stime(row[0])
                if not first_time:      
                    first_time = timestamp
                last_time = timestamp

                antenna_ = int(row[2])
                ten = self.rten(float(row[7]))

                data[antenna_].append([timestamp, ten])
                temp = float(row[6])

                # get min and max range of tension
                if min_y > ten:
                    min_y = ten
                elif max_y < ten:
                    max_y = ten

                if antenna != antenna_:
                    # calculate belt speed
                    if start_timestamp:
                        # print antenna, antenna_, '@@@@@@@2'
                        period = (timestamp - start_timestamp).total_seconds()
                        sp = DISTANCES[antenna-1] / period                    
                    start_timestamp = timestamp
                    # calculate # of cycles
                    if antenna > antenna_ and self.last_time < timestamp:
                        self.num_cycles +=1 #counting the number of frames
                    antenna = antenna_

            except Exception, e:
                pass

        self.last_time = last_time
        # min_y = max(0, min_y)
        # max_y = min(50, max_y)
        self.plot(data[1], 'c')     # Antenna 1
        self.plot(data[2], 'r')     # Antenna 2
        self.plot(data[3], 'y')     # Antenna 3

        #Filling the text boxes
        self.tx_temp.set_text(u"Temperature\n   {temp:.2f} °F".format(temp=self.deg2F(temp)))
        self.tx_time.set_text("   Time\n{}".format(datetime.now().strftime("%H:%M:%S")))
        self.tx_overdrive.set_text("Overdrive\n   ---------")
        self.tx_cycles.set_text("Cyles\n {cyles}".format(cyles=self.num_cycles)) 
        self.tx_drum.set_text("Drum Speed\n {}".format('   -----------') )
        self.tx_belt.set_text("Belt Speed\n {sp:.2f} (ft/s)".format(sp=sp) )        
        self.ax.set_ylim([int(min_y)-3, int(max_y)+3])     
        self.ax.set_xlim([matplotlib.dates.date2num(first_time), matplotlib.dates.date2num(last_time)])
        #Update the canvas
        self.fig.canvas.draw()

    def deg2F(self,deg):
        return float(deg) * 9./5. + 32. 

    def stime(self, timestamp):
        return datetime.strptime(timestamp, '%m/%d/%Y %H:%M:%S.%f')

    def rten(self, ten):
        return int(ten * self.slope + self.offset)

    def read_last_n_line(self):
        MAX_CHARS_PER_LINE = 100
        n = TIME_WINDOW * 54 * 2 
        size_of_file = os.path.getsize(self.file)
        file_handler = open(self.file, "r")
        seek_index = max(0, size_of_file - (n * MAX_CHARS_PER_LINE))
        file_handler.seek(seek_index)
        buffer_ = file_handler.read()
        file_handler.close()
        lines = buffer_.split('\n')[1:] 
        return lines


if __name__ == "__main__":
    Anim()