import os
import re
import random

from time import sleep
from datetime import datetime

INTERVAL_RANGE = [500, 700]
DATA_NUMBER_RANGE = [20, 35]
TEMPERATURE_RANGE = [2, 40]
TENSION_RANGE = [90, 250]

read_count = 100
data_number = random.randint(DATA_NUMBER_RANGE[0], DATA_NUMBER_RANGE[1])
antenna_number = 1

while(True):
    with open('./SensorLog.csv', 'a') as f1:
        interval = random.randint(INTERVAL_RANGE[0], INTERVAL_RANGE[1])
        sleep(interval / 1000.)

        time_stamp = datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")
        read_count += 1
        temperature = random.randint(TEMPERATURE_RANGE[0], TEMPERATURE_RANGE[1])
        tension = random.randint(TENSION_RANGE[0], TENSION_RANGE[1])
        data_number -= 1

        if data_number:     # use same antenna
            pass
        else:               # switch to another antenna
            # antenna_number = (antenna_number+1) % 3
            antenna_number = 1#random.randint(1, 3)
            data_number = random.randint(DATA_NUMBER_RANGE[0], DATA_NUMBER_RANGE[1])
            sleep(1.1)

        record = "{}, {}, {}, GEN2, -5, E036112D912508B3, {}, {}, 0, 3.38,  (Infinity%)," \
            .format(time_stamp, read_count, antenna_number, temperature, tension)
        f1.write(record + os.linesep)
        f1.close()