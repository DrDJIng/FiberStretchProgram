import math  # For sin
import struct
import sys  # For version_info and platform
import time  # For sleep, clock, time and perf_counter
from datetime import datetime  # For printing times with now
import scipy
from functools import partial
from datetime import datetime
from tkinter import *
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk )
from matplotlib.backend_bases import key_press_handler
import numpy as np
import queue
import threading
try:
    import LabJackPython
    import u6
    import u3
except:
    tkMessageBox.showerror("Driver error", '''The driver could not be imported.
# Please install the UD driver (Windows) or Exodriver (Linux and Mac OS X) from www.labjack.com''')

# Define main class that will contain all UI elements, threading control, etc. Going to store pretty much everything in self, so it should be available whenever threads update.
# I will send any pertinent data through queue's though, to avoid the possibility of race conditions, which shouldn't be an issue with what I'm doing anyway.
class MainUI:
    EEPROM_ADDRESS = 0x50
    DAC_ADDRESS = 0x12
    # Define the initialisation, which will initiate all GUI elements
    def __init__(self):
        global initCheck
        global lastInd
        global shouldPlotContinue
        plotCounter = 0
        initCheck = 0
        shouldPlotContinue = 1
        # Initialise data in memory
        self.forceData = []
        self.lengthData = []
        self.checkDataF = []
        self.checkDataL = []
        self.U6device = u6.U6()
        self.U6device.getCalibrationData()
        self.U3device = u3.U3()
        # For applying the proper calibration to readings.
        self.U3device.getCalibrationData()
        dioPin = 4
        # Configure FIO0 to FIO4 as analog inputs, and FIO04 to FIO7 as digital I/O.
        self.U3device.configIO(FIOAnalog=0x0F)


        self.sclPin = dioPin
        self.sdaPin = self.sclPin + 1

        data = self.U3device.i2c(MainUI.EEPROM_ADDRESS, [64],
                               NumI2CBytesToReceive=36, SDAPinNum=self.sdaPin,
                               SCLPinNum=self.sclPin)
        response = data['I2CBytes']
        self.slopeA = self.toDouble(response[0:8])
        self.offsetA = self.toDouble(response[8:16])
        self.slopeB = self.toDouble(response[16:24])
        self.offsetB = self.toDouble(response[24:32])

        if 255 in response:
            msg = "LJTick-DAC calibration constants seem off. Check that the " \
                  "LJTick-DAC is connected properly."
            raise Exception(msg)

        self.startUI()

    def startUI(self):
        # Set up UI system.
        self.root = Tk()
        self.root.title("Force measurements")
        Grid.rowconfigure(self.root, 0, weight = 1)
        Grid.columnconfigure(self.root, 0, weight = 1)

        self.mainFrame = ttk.Frame(self.root, borderwidth=5, relief="sunken")
        self.mainFrame.grid(column = 0, row = 0, sticky = (N, S, E, W))
        Grid.rowconfigure(self.mainFrame, 0, weight = 1)
        Grid.columnconfigure(self.mainFrame, 0, weight = 1)


        self.settingsFrame = ttk.Frame(self.mainFrame)
        self.settingsFrame.grid(column = 0, row = 1, sticky = (N, S, E, W))
        self.settingsFrame.columnconfigure(0, weight = 1)
        self.settingsFrame.columnconfigure(1, weight = 1)
        self.settingsFrame.columnconfigure(2, weight = 1)

        # Create buttons and place them in the setting frame.
        self.signalFrame = ttk.Frame(self.settingsFrame)
        self.signalFrame.grid(column = 0, row = 0)
        # Signal options
        self.raisesLabel = ttk.Label(self.signalFrame, text = 'Number of voltage raises')
        self.raisesLabel.grid(column = 0, row = 1)
        numRises = StringVar()
        self.nRises = ttk.Entry(self.signalFrame, textvariable = numRises)
        self.nRises.grid(column = 1, row = 1)
        self.nRises.insert(0, '1')
        # Signal buttons
        self.signalButton = ttk.Button(self.signalFrame, text = 'Send signal', command = partial(self.startNewThread, self.sendSignal))
        self.signalButton.grid(column = 2, row = 0)
        self.startButton = ttk.Button(self.signalFrame, text = 'Start measuring', command = partial(self.startNewThread, self.startStream))
        self.startButton.grid(column = 2, row = 1, pady = 10)
        self.stopButton = ttk.Button(self.signalFrame, text = 'Stop measuring', command = self.stopStream)
        self.stopButton.grid(column = 2, row = 2, pady = 10)

        # Stage buttons
        self.stageFrame = ttk.Frame(self.settingsFrame)
        self.stageFrame.grid(column = 1, row = 0)
        self.stageForwardButton = ttk.Button(self.stageFrame, text = 'Stage forward', command = partial(self.moveStage, 1))
        self.stageForwardButton.grid(column = 1, row = 2)
        self.stageBackwardButton = ttk.Button(self.stageFrame, text = 'Stage back', command = partial(self.moveStage, -1))
        self.stageBackwardButton.grid(column = 2, row = 2)

        # Other buttons
        self.otherFrame = ttk.Frame(self.settingsFrame)
        self.otherFrame.grid(column = 2, row = 0)
        self.exportButton = ttk.Button(self.otherFrame, text = 'Export data', command = self.exportData)
        self.exportButton.grid(column = 3, row = 0, pady = 10)
        self.calibrateButton = ttk.Button(self.otherFrame, text = 'Calibrate', command = self.setCalibration)
        self.calibrateButton.grid(column = 4, row = 0)


        self.plottingFrame = ttk.Frame(self.mainFrame)
        self.plottingFrame.grid(column = 0, row = 0, sticky = (N, S, E, W))
        Grid.rowconfigure(self.plottingFrame, 0, weight = 1)
        Grid.columnconfigure(self.plottingFrame, 0, weight = 1)

        # Might need to move entire figure creation, etc, into the thread so that it can be accessed properly? Not sure.
        self.plotFig = Figure(figsize=(19.2, 7.2), dpi = 100) # Have to take into account the DPI to set the inch sizes here. 100 dpi = 19.2 inches for a typical 1920x1080 screen.
        self.forceAxis = self.plotFig.add_subplot(2, 1, 1)
        self.lengthAxis = self.plotFig.add_subplot(2, 1, 2)
        self.forceAxis.set_ylim([-10, 10]) # Set the y-axis limits to -10 and 10, the range of the transducer (might actually be -5 to 5, need to check).
        self.lengthAxis.set_ylim([-10, 10])
        self.plotFig.set_tight_layout(True) # Get rid of that annoying whitespace.
        self.canvas = FigureCanvasTkAgg(self.plotFig, self.plottingFrame) # Tell TKinter which frame to put the canvas into
        self.canvas.get_tk_widget().grid(row = 0, column = 0, sticky = (N, S, E, W)) # Assign grid coordinates within the previous frame
        self.canvas.draw() # Draw the canvas.

        # Start mainloop, which activates the window
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.mainloop()

    # Function to start a new threads
    def startNewThread(self, funcname):
        if funcname == self.startStream:
            self.streamThread = threading.Thread(target = funcname)
            self.streamThread.start()
            self.updateGraph()
        else:
            self.signalThread = threading.Thread(target = funcname)
            self.signalThread.start()

    def updateGraph(self):
        global initCheck
        global lastInd
        global shouldPlotContinue
        if len(self.forceData) > 0:
            # Need to add in timer here for X-data, involves learning how to use Labjack timer
            self.forceAxis.clear()
            self.lengthAxis.clear()
            self.forceAxis.set_ylim([-11, 11])
            self.lengthAxis.set_ylim([-11, 11])

            # Check to see if data has changed. Will need to come up with better way to do this if / when memory becomes an issue.
            if (self.forceData != self.checkDataF) or (self.lengthData != self.checkDataL):
                if initCheck == 0:
                    initCheck = 1
                    xlim = (np.arange(len(self.forceData)) + 1) * 1 / 200
                    self.forceAxis.plot(xlim, self.forceData, color='blue')
                    self.lengthAxis.plot(xlim, self.lengthData, color='blue')
                    self.forceAxis.set_xlim([xlim[0], xlim[-1]])
                    self.lengthAxis.set_xlim([xlim[0], xlim[-1]])
                    lastInd = xlim[-1]
                    print(lastInd)
                    self.forceAxis.set_xticks((np.arange(len(self.forceData), step = 20) + 1) * 1 / 200)
                    self.lengthAxis.set_xticks((np.arange(len(self.forceData), step = 20) + 1) * 1 / 200)
                else:
                    xlim = lastInd + (np.arange(len(self.forceData[-200:])) + 1) * 1 / 200
                    self.forceAxis.plot(xlim, self.forceData[-200:], color='blue')
                    self.lengthAxis.plot(xlim, self.lengthData[-200:], color='blue')
                    self.forceAxis.set_xlim([xlim[0], xlim[-1]])
                    self.lengthAxis.set_xlim([xlim[0], xlim[-1]])
                    self.forceAxis.set_xticks(lastInd + (np.arange(len(self.forceData[-200:]), step = 20) + 1) * 1 / 200)
                    self.lengthAxis.set_xticks(lastInd + (np.arange(len(self.forceData[-200:]), step = 20) + 1) * 1 / 200)
                    lastInd = xlim[-1]

                self.canvas.draw()
                self.checkDataF = self.forceData
                self.checkDataL = self.lengthData

        if shouldPlotContinue == 0:
            # Set plots after stopping to an overall view of data (This happens anyway in an uncontrolled fashion, set here so it's controlled.)
            self.forceAxis.clear()
            self.lengthAxis.clear()
            self.forceAxis.set_ylim([-11, 11])
            self.lengthAxis.set_ylim([-11, 11])
            xlim = (np.arange(len(self.forceData)) + 1) * 1 / 200
            self.forceAxis.plot(xlim, self.forceData, color='blue')
            self.lengthAxis.plot(xlim, self.lengthData, color='blue')
            self.forceAxis.set_xlim([xlim[0], xlim[-1]])
            self.lengthAxis.set_xlim([xlim[0], xlim[-1]])
            stepper = round(len(self.forceData)/20)
            self.forceAxis.set_xticks((np.arange(len(self.forceData), step = stepper) + 1) * 1 / 200)
            self.lengthAxis.set_xticks((np.arange(len(self.forceData), step = stepper) + 1) * 1/ 200)
            self.canvas.draw()
        elif shouldPlotContinue == 1:
            self.root.after(50, self.updateGraph)

    # Set up the LabJack and start the streaming process
    def startStream(self):
        global shouldPlotContinue
        global streamStopper
        streamStopper = 0 # To stop the streaming/thread.

        print('Starting data stream...')

        print("Configuring U6 stream")

        # Set scan frequency to 2x double what we want actual frequency to be at. Could probably do this non-stream, but two channels at 100Hz feels like a streaming problem to me.  Attach to an editable field at some point.
        SCAN_FREQUENCY = 2000

        # Set up the stream from Labjack U6
        self.U6device.streamConfig(NumChannels=2, ChannelNumbers=[0, 1], ChannelOptions=[0, 0], SettlingFactor=1, ResolutionIndex=3, ScanFrequency=SCAN_FREQUENCY)
        while streamStopper == 0:
            print("Start stream")
            self.U6device.streamStart()
            start = datetime.now()
            print("Start time is %s" % start)

            missed = 0
            dataCount = 0
            packetCount = 0

            for r in self.U6device.streamData():
                if r is not None:
                    # Our stop condition
                    if streamStopper == 1:
                        break

                    if r["errors"] != 0:
                        print("Errors counted: %s ; %s" % (r["errors"], datetime.now()))

                    if r["numPackets"] != self.U6device.packetsPerRequest:
                        print("----- UNDERFLOW : %s ; %s" %
                            (r["numPackets"], datetime.now()))

                    if r["missed"] != 0:
                        missed += r['missed']
                        print("+++ Missed %s" % r["missed"])

                    # Update y-axis data to plot, auto-axis should keep it within range
                    updateData = r["AIN0"]
                    # Append onto all data, for export later
                    self.forceData = self.forceData + r["AIN0"]
                    self.lengthData = self.lengthData + r["AIN1"]

                    dataCount += 1
                    packetCount += r['numPackets']

                else:
                    # Got no data back from our read.
                    # This only happens if your stream isn't faster than the USB read
                    # timeout, ~1 sec.
                    print("No data ; %s" % datetime.now())

        self.U6device.streamStop()
        print("Stream stopped.\n")
        return

    # Function to stop the automatic retrieval and plotting of data.
    def stopStream(self):
        global streamStopper
        global plotCounter
        global initCheck
        global shouldPlotContinue

        streamStopper = 1 # Stop the stream
        plotCounter = 0 # Reset plot counter for accurate timing
        initCheck = 0 # Reset initial check for plotting
        shouldPlotContinue = 0 # Stop plotting
        print(self.lengthData)

    # Function to send signal to the motors, generalised such that it can send a signal to either the stage motor (SM) or force motor (FM).
    def sendSignal(self):
        # dacA = 2.2
        # binaryA = int(dacA*self.slopeA + self.offsetA)
        # self.U3device.i2c(MainUI.DAC_ADDRESS,
        #                 [48, binaryA // 256, binaryA % 256],
        #                 SDAPinNum=self.sdaPin, SCLPinNum=self.sclPin)
        # time.sleep(0.01)
        # dacA = -2.2
        # binaryA = int(dacA*self.slopeA + self.offsetA)
        # self.U3device.i2c(MainUI.DAC_ADDRESS,
        #                 [48, binaryA // 256, binaryA % 256],
        #                 SDAPinNum=self.sdaPin, SCLPinNum=self.sclPin)

        # Create sine wave generator
        t = 0
        step = 0.01
        while t < 10:
            t += step
            value = 2*math.sin(math.pi * t)
            print(value)
            binaryA = int(value*self.slopeA + self.offsetA)
            self.U3device.i2c(MainUI.DAC_ADDRESS, [48, binaryA // 256, binaryA % 256],
                            SDAPinNum=self.sdaPin, SCLPinNum=self.sclPin)
            time.sleep(0.02)
        self.U3device.i2c(MainUI.DAC_ADDRESS, [48, 0 // 256, 0 % 256],
                        SDAPinNum=self.sdaPin, SCLPinNum=self.sclPin)
        return

    # Finally, an export function to write the data from streaming to the disk.
    def exportData(self):
        print('Exporting data...')

    # Need a function to set the calibration of the voltages we're getting from the force transducer.
    def setCalibration(self):
        print('Setting calibration...')

    # This function will set the motor strength
    def setMotor(self):
        pass

    # This function will move the stage
    def moveStage(self, direction):
        if direction == 1:
            print('Moving stage forward')
        else:
            print('Moving stage backward')

    def toDouble(self, buff):
        """Converts the 8 byte array into a floating point number.
        buff: An array with 8 bytes.

        """
        right, left = struct.unpack("<Ii", struct.pack("B" * 8, *buff[0:8]))
        return float(left) + float(right)/(2**32)

    # A close function, to stop any active threads in the proper way, close the device, and close the window.
    def close(self):
        try:
            self.U6device.streamStop()
            self.U6device.close()
            if self.thread is not None:
                self.thread.stop()
                self.thread.join()
                print("Threads closed.")
            if self.U6device is not None:
                self.U6device.close()
                print("Device closed.")
        except:
            print("Thanks for using!")
        finally:
            self.root.quit()
            self.root.destroy()
if __name__ == '__main__':
    MainUI()
