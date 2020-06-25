import sys
from datetime import datetime
import tkinter as Tkinter
import tkinter.messagebox as tkMessageBox
import matplotlib
matplotlib.use("TkAgg") # Need to change this for some reason
# Import extras from matplotplib for use with Tkinter in the GUI
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk )
from matplotlib.figure import Figure
import numpy as np
font = {'size'   : 4}
matplotlib.rc('font', **font)


# Need a queue for threads, etc.
from queue import Queue

# Define and setup the main window class, which includes the entire application.
class MainWindow:
    """
    The main window of the application
    """

    FONT_SIZE = 10
    FONT = "Arial"

    def __init__(self):
        # Basic setup
        self.window = Tkinter.Tk()
        self.window.title("Guth machine")
        self.settingsFrame = Tkinter.Frame(height=1080, width=480, bd=1, relief=Tkinter.SUNKEN)
        self.settingsFrame.pack(side=Tkinter.LEFT)
        self.graphsFrame = Tkinter.Frame(height=1080, width=1440, bd=1, relief=Tkinter.SUNKEN)
        self.graphsFrame.pack(side=Tkinter.RIGHT)

        self.forceFig = Figure(figsize=(4.8, 1.6), dpi=300)
        self.plotter = self.forceFig.add_subplot(1, 1, 1)
        self.plotter.set_ylim([-10, 10])
        self.canvas = FigureCanvasTkAgg(self.forceFig, self.graphsFrame)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.canvas.draw()

        # Buttons frame
        self.startButton = Tkinter.Button(self.settingsFrame, text="Start", command=self.start, font=(MainWindow.FONT, MainWindow.FONT_SIZE))
        self.startButton.grid(row=0, column=0)

        # Ensure the exsistance of a thread, queue, and device variable
        self.targetQueue = Queue()
        self.thread = None
        self.device = None

        # Determine if we are reading data
        self.reading = False

        # Start mainloop
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.mainloop()

    def close(self):
        try:
            if self.thread is not None:
                self.thread.stop()
                self.thread.join()
            if self.device is not None:
                self.device.close()
        except:
            print("Error terminating app")
        finally:
            self.window.destroy()

    def start(self):
        self.ydata = []
        # Setup the U6
        try:
            import LabJackPython
            import u6
        except:
            tkMessageBox.showerror("Driver error", '''The driver could not be imported.
        Please install the UD driver (Windows) or Exodriver (Linux and Mac OS X) from www.labjack.com''')

        # At high frequencies ( >5 kHz), the number of samples will be MAX_REQUESTS
        # times 48 (packets per request) times 25 (samples per packet).
        self.device = u6.U6()

        # For applying the proper calibration to readings.
        self.device.getCalibrationData()

        print("Configuring U6 stream")

        # Set scan frequency to 2x double what we want actual frequency to be at. Could probably do this non-stream, but two channels at 100Hz feels like a streaming problem to me.  Attach to an editable field at some point.
        SCAN_FREQUENCY = 400
        MAX_REQUESTS = 10
        # Set up the stream from Labjack U6
        self.device.streamConfig(NumChannels=2, ChannelNumbers=[0, 1], ChannelOptions=[0, 0], SettlingFactor=1, ResolutionIndex=3, ScanFrequency=SCAN_FREQUENCY)
        try:
            print("Start stream")
            self.device.streamStart()
            start = datetime.now()
            print("Start time is %s" % start)

            missed = 0
            dataCount = 0
            packetCount = 0

            for r in self.device.streamData():
                if r is not None:
                    # Our stop condition
                    if dataCount >= MAX_REQUESTS:
                        break

                    if r["errors"] != 0:
                        print("Errors counted: %s ; %s" % (r["errors"], datetime.now()))

                    if r["numPackets"] != self.device.packetsPerRequest:
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
                    self.ydata = self.ydata + r["AIN0"]

        #             Need to add in timer here for X-data, involves learning how to use Labjack timer
                    self.plotter.clear()
                    self.plotter.set_ylim([-10, 10])
                    self.plotter.plot(np.arange(len(updateData)), updateData, color='blue')
                    self.canvas.draw()

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
            self.device.streamStop()
            print("Stream stopped.\n")
            self.device.close()

            sampleTotal = packetCount * self.device.streamSamplesPerPacket

            scanTotal = sampleTotal / 2  # sampleTotal / NumChannels
            # print("%s requests with %s packets per request with %s samples per packet = %s samples total." %
                # (dataCount, (float(packetCount)/dataCount), self.device.streamSamplesPerPacket, sampleTotal))
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
            # plt.show(block=True)

MainWindow()
