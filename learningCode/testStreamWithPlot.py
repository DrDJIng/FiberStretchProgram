import sys
import traceback
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

import u6


# MAX_REQUESTS is the number of packets to be read.
MAX_REQUESTS = 10
# SCAN_FREQUENCY is the scan frequency of stream mode in Hz
SCAN_FREQUENCY = 4000

d = None

# Prepare axis for plotting
fig = plt.figure()
# Not quite sure what this does
ax = fig.add_subplot(111)

# draw and show it
ax.relim()
# Turn on autoscaling in both x and y directions
ax.autoscale_view(True,False,True)
ax.set_ylim([-10,10])

# Draw the canvas
fig.canvas.draw()
# Turn off blocking of computation while plot is up, make plot interactive
plt.ion()
# Show the plot
plt.show()
###############################################################################
# U6
# Uncomment these lines to stream from a U6
###############################################################################

# At high frequencies ( >5 kHz), the number of samples will be MAX_REQUESTS
# times 48 (packets per request) times 25 (samples per packet).
d = u6.U6()

# For applying the proper calibration to readings.
d.getCalibrationData()

DAC0_VALUE = d.voltageToDACBits(1.5, dacNumber = 0, is16Bits = False)
d.getFeedback(u6.DAC0_8(DAC0_VALUE))

print("Configuring U6 stream")

d.streamConfig(NumChannels=1, ChannelNumbers=[0], ChannelOptions=[0], SettlingFactor=1, ResolutionIndex=3, ScanFrequency=SCAN_FREQUENCY)

ydata = []

if d is None:
    print("""Configure a device first.
Please open streamTest.py in a text editor and uncomment the lines for your device.

Exiting...""")
    sys.exit(0)

try:
    print("Start stream")
    d.streamStart()
    start = datetime.now()
    print("Start time is %s" % start)

    missed = 0
    dataCount = 0
    packetCount = 0

    for r in d.streamData():
        if r is not None:
            # Our stop condition
            if dataCount >= MAX_REQUESTS:
                break

            if r["errors"] != 0:
                print("Errors counted: %s ; %s" % (r["errors"], datetime.now()))

            if r["numPackets"] != d.packetsPerRequest:
                print("----- UNDERFLOW : %s ; %s" %
                      (r["numPackets"], datetime.now()))

            if r["missed"] != 0:
                missed += r['missed']
                print("+++ Missed %s" % r["missed"])

            # Comment out these prints and do something with r
            print("Average of %s AIN0 readings: %s" %
                  (len(r["AIN0"]), sum(r["AIN0"])/len(r["AIN0"])))

#             Update y-axis data to plot, auto-axis should keep it within range
            updateData = r["AIN0"]
            # Append onto all data, for export later
            ydata = ydata + r["AIN0"]

#             Need to add in timer here for X-data, involves learning how to use Labjack timer
            plt.cla()
            ax.plot(np.arange(len(updateData)), updateData, color='blue')
            plt.draw()
            plt.pause(0.0001)

            dataCount += 1
            packetCount += r['numPackets']
        else:
            # Got no data back from our read.
            # This only happens if your stream isn't faster than the USB read
            # timeout, ~1 sec.
            print("No data ; %s" % datetime.now())
except:
    print("".join(i for i in traceback.format_exc()))
finally:
    stop = datetime.now()
    d.streamStop()
    print("Stream stopped.\n")
    d.close()

    sampleTotal = packetCount * d.streamSamplesPerPacket

    scanTotal = sampleTotal / 2  # sampleTotal / NumChannels
    # print("%s requests with %s packets per request with %s samples per packet = %s samples total." %
          # (dataCount, (float(packetCount)/dataCount), d.streamSamplesPerPacket, sampleTotal))
    print("%s samples were lost due to errors." % missed)
    sampleTotal -= missed
    print("Adjusted number of samples = %s" % sampleTotal)

    runTime = (stop-start).seconds + float((stop-start).microseconds)/1000000
    print("The experiment took %s seconds." % runTime)
    print("Actual Scan Rate = %s Hz" % SCAN_FREQUENCY)
    print("Timed Scan Rate = %s scans / %s seconds = %s Hz" %
          (scanTotal, runTime, float(scanTotal)/runTime))
    print("Timed Sample Rate = %s samples / %s seconds = %s Hz" %
          (sampleTotal, runTime, float(sampleTotal)/runTime))
    plt.show(block=True)