import math  # For sin
import struct
import sys  # For version_info and platform
import time  # For sleep, clock, time and perf_counter
import os
import csv
from datetime import datetime  # For printing times with now
import scipy
from functools import partial
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
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
    # Define the initialisation, which will initiate all GUI elements
    def __init__(self):
        print(os.path.dirname(os.path.realpath(__file__)))
        # LOAD CALIBRATION FROM FILE
        self.forceCalibration = 1
        # Set scan frequency to 2x double what we want actual frequency to be at. Could probably do this non-stream, but two channels at 100Hz feels like a streaming problem to me.  Attach to an editable field at some point.
        self.SCAN_FREQUENCY = 1000
        global initCheck
        global lastInd
        global shouldPlotContinue
        plotCounter = 0
        initCheck = 0
        shouldPlotContinue = 1
        # Initialise data in memory
        self.forceData = []
        self.lengthData = []
        self.signalData = []
        self.otherData = []
        self.checkDataF = []
        self.checkDataL = []
        self.U6device = u6.U6()
        self.U6device.getCalibrationData()
        self.U3device = u3.U3()
        # For applying the proper calibration to readings.
        self.U3device.getCalibrationData()
        # self.setLJTick()
        self.startUI()

    def startUI(self):
        # Set up UI system.
        self.root = Tk()
        self.root.state('zoomed')
        self.root.title("Force measurements")
        Grid.rowconfigure(self.root, 0, weight = 1)
        Grid.columnconfigure(self.root, 0, weight = 1)
        numRises = StringVar()
        disMove = StringVar()
        calWeight = StringVar()
        calForce = StringVar()
        pulLen = StringVar()
        exName = StringVar()
        exPoints = StringVar()
        fLimU = StringVar()
        fLimD = StringVar()
        lLimU = StringVar()
        lLimD = StringVar()
        sLimU = StringVar()
        sLimD = StringVar()

        self.mainFrame = ttk.Frame(self.root, borderwidth=5, relief="sunken")
        self.mainFrame.grid(column = 0, row = 0, sticky = (N, S, E, W))
        Grid.rowconfigure(self.mainFrame, 0, weight = 1)
        Grid.columnconfigure(self.mainFrame, 0, weight = 1)


        self.settingsFrame = ttk.Frame(self.mainFrame)
        self.settingsFrame.grid(column = 0, row = 1, sticky = (N, S, E, W))
        self.settingsFrame.columnconfigure(0, weight = 1)
        self.settingsFrame.columnconfigure(1, weight = 1)
        self.settingsFrame.columnconfigure(2, weight = 1)
        self.settingsFrame.columnconfigure(3, weight = 1)
        self.settingsFrame.columnconfigure(4, weight = 1)

        # Create buttons and place them in the setting frame.
        self.signalSetsFrame = ttk.Frame(self.settingsFrame)
        self.signalSetsFrame.grid(column = 0, row = 0)
        # Signal options
        self.moveLabel = ttk.Label(self.signalSetsFrame, text = 'Move distance (mm)')
        self.moveLabel.grid(column = 0, row = 0)
        self.disMove = ttk.Entry(self.signalSetsFrame, textvariable = disMove, width = 5, justify = CENTER)
        self.disMove.grid(column = 1, row = 0)
        self.disMove.insert(0, '1')
        self.timeLabel = ttk.Label(self.signalSetsFrame, text = 'Pulse length (s)')
        self.timeLabel.grid(column = 0, row = 1)
        self.pulTime = ttk.Entry(self.signalSetsFrame, textvariable = pulLen, width = 5, justify = CENTER)
        self.pulTime.grid(column = 1, row = 1)
        self.pulTime.insert(0, '1')
        self.raisesLabel = ttk.Label(self.signalSetsFrame, text = 'Number of voltage raises')
        self.raisesLabel.grid(column = 0, row = 2)
        self.nRises = ttk.Entry(self.signalSetsFrame, textvariable = numRises, width = 5, justify = CENTER)
        self.nRises.grid(column = 1, row = 2)
        self.nRises.insert(0, '1')

        # Create buttons and place them in the signal frame.
        self.signalFrame = ttk.Frame(self.settingsFrame)
        self.signalFrame.grid(column = 1, row = 0)
        self.moveLabel = ttk.Label(self.signalFrame, text = "Frequency set to: %s" % self.SCAN_FREQUENCY)
        self.moveLabel.grid(column = 0, row = 0)
        self.signalButton = ttk.Button(self.signalFrame, text = 'Send signal', command = partial(self.startNewThread, self.sendSignal))
        self.signalButton.grid(column = 0, row = 2, pady = 10)
        self.startButton = ttk.Button(self.signalFrame, text = 'Start measuring', command = partial(self.startNewThread, self.startStream))
        self.startButton.grid(column = 0, row = 3, pady = 10)
        self.stopButton = ttk.Button(self.signalFrame, text = 'Stop measuring', command = self.stopStream)
        self.stopButton.grid(column = 0, row = 4, pady = 10)

        # Stage buttons
        self.stageFrame = ttk.Frame(self.settingsFrame)
        self.stageFrame.grid(column = 2, row = 0)
        self.stageForwardButton = ttk.Button(self.stageFrame, text = 'Stage forward', command = partial(self.moveStage, 1))
        self.stageForwardButton.grid(column = 1, row = 2)
        self.stageBackwardButton = ttk.Button(self.stageFrame, text = 'Stage back', command = partial(self.moveStage, -1))
        self.stageBackwardButton.grid(column = 2, row = 2)

        # Other buttons
        self.exportFrame = ttk.Frame(self.settingsFrame)
        self.exportFrame.grid(column = 3, row = 0)
        self.exNameLabel = ttk.Label(self.exportFrame, text = 'Export name:')
        self.exNameLabel.grid(column = 0, row = 0)
        self.exportName = ttk.Entry(self.exportFrame, textvariable = exName)
        self.exportName.grid(column = 1, row = 0)
        self.exportName.insert(0, 'output')
        self.exPointLabel = ttk.Label(self.exportFrame, text = 'Only save every nth point:')
        self.exPointLabel.grid(column = 0, row = 1)
        self.exportPoints = ttk.Entry(self.exportFrame, textvariable = exPoints, width = 3, justify = CENTER)
        self.exportPoints.grid(column = 1, row = 1)
        self.exportPoints.insert(0, '100')
        self.exportButton = ttk.Button(self.exportFrame, text = 'Export data', command = self.exportData)
        self.exportButton.grid(column = 1, row = 2)

        # Calibrate buttons
        self.calibrateFrame = ttk.Frame(self.settingsFrame)
        self.calibrateFrame.grid(column = 4, row = 0)
        self.calibrateButton = ttk.Button(self.calibrateFrame, text = 'Calibrate', command = self.setCalibration)
        self.calibrateButton.grid(column = 1, row = 2)
        self.calWeight = ttk.Entry(self.calibrateFrame, textvariable = calWeight, width = 3, justify = CENTER)
        self.calWeight.grid(column = 1, row = 0)
        self.calWeight.insert(0, '3')
        self.calForce = ttk.Entry(self.calibrateFrame, textvariable = calForce, width = 3, justify = CENTER)
        self.calForce.grid(column = 1, row = 1)
        self.calForce.insert(0, '2')

        self.plotFrame = ttk.Frame(self.mainFrame)
        self.plotFrame.grid(column = 0, row = 0, sticky = (N, S, E, W))
        Grid.rowconfigure(self.plotFrame, 0, weight = 1)
        Grid.columnconfigure(self.plotFrame, 1, weight = 1)

        self.plottingFrame = ttk.Frame(self.plotFrame)
        self.plottingFrame.grid(column = 1, row = 0, sticky = (N, S, E, W))
        Grid.rowconfigure(self.plottingFrame, 0, weight = 1)
        Grid.columnconfigure(self.plottingFrame, 1, weight = 1)

        # Might need to move entire figure creation, etc, into the thread so that it can be accessed properly? Not sure.
        self.plotFig = Figure(figsize=(15.8, 7.2), dpi = 100) # Have to take into account the DPI to set the inch sizes here. 100 dpi = 19.2 inches for a typical 1920x1080 screen.
        self.forceAxis = self.plotFig.add_subplot(3, 1, 1)
        self.lengthAxis = self.plotFig.add_subplot(3, 1, 2)
        self.signalAxis = self.plotFig.add_subplot(3, 1, 3)

        # self.otherAxis.set_ylim([-10, 10])
        self.plotFig.set_tight_layout(True) # Get rid of that annoying whitespace.
        self.canvas = FigureCanvasTkAgg(self.plotFig, self.plottingFrame) # Tell TKinter which frame to put the canvas into
        self.canvas.get_tk_widget().grid(row = 0, column = 0, sticky = (N, S, E, W)) # Assign grid coordinates within the previous frame
        self.toolbarFrame = ttk.Frame(self.plottingFrame)
        self.toolbarFrame.grid(column = 0, row = 1)
        self.canvasNav = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)


        self.limFrame = ttk.Frame(self.plotFrame)
        self.limFrame.grid(column = 0, row = 0, sticky = (N, S, E, W))
        Grid.rowconfigure(self.limFrame, 0, weight = 1)
        Grid.rowconfigure(self.limFrame, 1, weight = 1)
        Grid.rowconfigure(self.limFrame, 2, weight = 1)
        Grid.rowconfigure(self.limFrame, 3, weight = 1)
        Grid.rowconfigure(self.limFrame, 4, weight = 1)
        Grid.rowconfigure(self.limFrame, 5, weight = 1)

        self.fLimUp = ttk.Entry(self.limFrame, textvariable = fLimU, width = 3, justify = CENTER)
        self.fLimUp.grid(column = 0, row = 0)
        self.fLimUp.insert(0, '10')
        self.fLimDown = ttk.Entry(self.limFrame, textvariable = fLimD, width = 3, justify = CENTER)
        self.fLimDown.grid(column = 0, row = 1)
        self.fLimDown.insert(0, '-1')
        self.lLimUp = ttk.Entry(self.limFrame, textvariable = lLimU, width = 3, justify = CENTER)
        self.lLimUp.grid(column = 0, row = 2)
        self.lLimUp.insert(0, '4')
        self.lLimDown = ttk.Entry(self.limFrame, textvariable = lLimD, width = 3, justify = CENTER)
        self.lLimDown.grid(column = 0, row = 3)
        self.lLimDown.insert(0, '0')
        self.sLimUp = ttk.Entry(self.limFrame, textvariable = sLimU, width = 3, justify = CENTER)
        self.sLimUp.grid(column = 0, row = 4)
        self.sLimUp.insert(0, '6')
        self.sLimDown = ttk.Entry(self.limFrame, textvariable = sLimD, width = 3, justify = CENTER)
        self.sLimDown.grid(column = 0, row = 5)
        self.sLimDown.insert(0, '0')

        # self.otherAxis = self.plotFig.add_subplot(4, 1, 4)
        self.forceAxis.set_ylim([int(self.fLimDown.get()), int(self.fLimUp.get())]) # Set the y-axis limits to -10 and 10, the range of the transducer (might actually be -5 to 5, need to check).
        self.lengthAxis.set_ylim([int(self.lLimDown.get()), int(self.lLimUp.get())])
        self.signalAxis.set_ylim([int(self.sLimDown.get()), int(self.sLimUp.get())])

        self.canvas.draw() # Draw the canvas.
        self.canvasNav.update()
        # Start mainloop, which activates the window
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.mainloop()

    # Function to start a new threads
    def startNewThread(self, funcname):
        global shouldPlotContinue
        if funcname == self.startStream:
            self.streamThread = threading.Thread(target = funcname)
            self.streamThread.start()
            shouldPlotContinue = 1
            self.updateGraph()
        else:
            self.signalThread = threading.Thread(target = funcname)
            self.signalThread.start()

    def LimChange(self, direction, axis):
        pass

    def updateGraph(self):
        global initCheck
        global lastInd
        global shouldPlotContinue

        PLOT_LENGTH = round(self.SCAN_FREQUENCY / 2)
        if len(self.forceData) > 0:
            # Need to add in timer here for X-data, involves learning how to use Labjack timer
            self.forceAxis.clear()
            self.lengthAxis.clear()
            self.signalAxis.clear()

            fU = self.fLimUp.get()
            fD = self.fLimDown.get()
            lU = self.lLimUp.get()
            lD = self.lLimDown.get()
            sU = self.sLimUp.get()
            sD = self.sLimDown.get()

            if not fU or not fD or not lU or not lD or not sU or not sD:
                self.forceAxis.set_ylim([-1, 10]) # Set the y-axis limits to -10 and 10, the range of the transducer (might actually be -5 to 5, need to check).
                self.lengthAxis.set_ylim([0, 4])
                self.signalAxis.set_ylim([0, 6])
            else:
                fU = float(self.fLimUp.get())
                fD = float(self.fLimDown.get())
                lU = float(self.lLimUp.get())
                lD = float(self.lLimDown.get())
                sU = float(self.sLimUp.get())
                sD = float(self.sLimDown.get())
                self.forceAxis.set_ylim([fD, fU]) # Set the y-axis limits to -10 and 10, the range of the transducer (might actually be -5 to 5, need to check).
                self.lengthAxis.set_ylim([lD, lU])
                self.signalAxis.set_ylim([sD, sU])
            # Check to see if data has changed. Will need to come up with better way to do this if / when memory becomes an issue.
            # I think I can do this using queueing, which I should implement. Also implement blitting for speed.
            # There is a weird delay when re-initialising the graphing, need to hunt that down.
            if (self.forceData != self.checkDataF) or (self.lengthData != self.checkDataL):
                if initCheck == 0:
                    initCheck = 1
                    self.forceAxis.plot(self.forceData, color='blue')
                    self.lengthAxis.plot(self.lengthData, color='blue')
                    self.signalAxis.plot(self.signalData, color='blue')
                else:
                    if len(self.forceData) > 100000:
                        self.forceAxis.plot(self.forceData[(len(self.forceData) - 100000):], color='blue')
                        self.lengthAxis.plot(self.lengthData[(len(self.lengthData) - 100000):], color='blue')
                        self.signalAxis.plot(self.signalData[(len(self.signalData) - 100000):], color='blue')
                    else:
                        self.forceAxis.plot(self.forceData, color='blue')
                        self.lengthAxis.plot(self.lengthData, color='blue')
                        self.signalAxis.plot(self.signalData, color='blue')
                    # lastInd = xlim[-1]

                self.canvas.draw()
                self.checkDataF = self.forceData
                self.checkDataL = self.lengthData

        if shouldPlotContinue == 0:
            # pass
            # Set plots after stopping to an overall view of data (This happens anyway in an uncontrolled fashion, set here so it's controlled.)
            self.endPlot(self.forceAxis, self.forceData)
            self.endPlot(self.lengthAxis, self.lengthData)
            self.endPlot(self.signalAxis, self.signalData)
            self.canvas.draw()
        elif shouldPlotContinue == 1:
            self.root.after(50, self.updateGraph)

    def endPlot(self, plotAxis, plotData):
        plotAxis.clear()
        xlim = np.arange(len(plotData)) * 1 / self.SCAN_FREQUENCY
        plotAxis.plot(xlim, plotData, color='blue')
        plotAxis.set_xlim([xlim[0], xlim[-1]])
        stepper = round(len(self.forceData)/20)
        plotAxis.set_xticks(np.arange(len(plotData), step = stepper) * 1 / self.SCAN_FREQUENCY)

    # Set up the LabJack and start the streaming process
    def startStream(self):
        global shouldPlotContinue
        global streamStopper
        streamStopper = 0 # To stop the streaming/thread.
        self.startButton.state(["disabled"])

        print('Starting data stream...')

        print("Configuring U6 stream")

        # Set up the stream from Labjack U6
        self.U6device.streamConfig(NumChannels=3, ChannelNumbers=[0, 1, 2], ChannelOptions=[0, 0, 0], SettlingFactor=1, ResolutionIndex=4, ScanFrequency=self.SCAN_FREQUENCY)
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
                    self.forceData = self.forceData + [self.forceCalibration * i for i in r["AIN0"]]
                    self.lengthData = self.lengthData + r["AIN1"]
                    self.signalData = self.signalData + r["AIN2"]
                    # self.otherData = self.otherData + r["AIN3"]

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
        self.streamThread.join()
        self.startButton.state(["!disabled"])

    # Function to send signal to the motors, generalised such that it can send a signal to either the stage motor (SM) or force motor (FM).
    def sendSignal(self):
        # Set voltages, then after sleep, reset to 0.
        # NEED TO ADD CONVERSION FROM/TO mm HERE. WHAT V = WHAT mm?
        print("Sending Signal")
        CONST_YELLOW = 3.8
        PULSE_LENGTH = float(self.pulTime.get())
        nSteps = int(self.nRises.get())
        STRETCH_LENGTH = float(self.disMove.get()) # eventually needs to be lengthChange * self.LengthToVolts
        stepNum = 1

        if STRETCH_LENGTH > 3.5 or STRETCH_LENGTH < 0:
            messagebox.showerror(
            "Setting stretch length",
            "Stretch length must be between 0 and 3.5 mm.\n(%s)" % STRETCH_LENGTH)
        elif nSteps < 1:
            messagebox.showerror(
            "Setting step number",
            "Voltage can only increase be positive integer amounts.\n(%s)" % nSteps)
        else:
            DAC0_VALUE = self.U3device.voltageToDACBits(STRETCH_LENGTH/nSteps, dacNumber = 1, is16Bits = False)
            self.U3device.getFeedback(u3.DAC0_8(DAC0_VALUE))
            time.sleep(0.2)
            DAC1_VALUE = self.U3device.voltageToDACBits(CONST_YELLOW, dacNumber = 1, is16Bits = False)
            self.U3device.getFeedback(u3.DAC1_8(DAC1_VALUE))

            while stepNum <= nSteps:
                if stepNum == 1:
                    stepNum += 1
                    time.sleep(PULSE_LENGTH)
                else:
                    currentValue = stepNum * STRETCH_LENGTH / nSteps
                    DAC0_VALUE = self.U3device.voltageToDACBits(currentValue, dacNumber = 1, is16Bits = False)
                    self.U3device.getFeedback(u3.DAC0_8(DAC0_VALUE))
                    time.sleep(PULSE_LENGTH)
                    stepNum += 1


            DAC1_VALUE = self.U3device.voltageToDACBits(0, dacNumber = 1, is16Bits = False)
            self.U3device.getFeedback(u3.DAC1_8(DAC1_VALUE))

    # Finally, an export function to write the data from streaming to the disk.
    def exportData(self):
        n = int(self.exportPoints.get())
        forceOutput = self.forceData[0::n]
        lengthOutput = self.lengthData[0::n]
        signalOutput = self.signalData[0::n]
        time = np.arange(len(self.forceData))*1/self.SCAN_FREQUENCY
        timeOutput = time[0::n]
        outputArray = zip(timeOutput, self.forceData, self.lengthData, self.signalData)
        if not os.path.exists('./outputs'):
                os.makedirs('./outputs')
        with open("./outputs/" + self.exportName.get() + ".csv", "w", newline = "") as f:
            writer = csv.writer(f)
            writer.writerows(outputArray)
            f.flush()

    # Need a function to set the calibration of the voltages we're getting from the force transducer.
    def setCalibration(self):
        # IF CALIBRATION DOESN'T EXIST
        POINT1 = [0,0]
        y1 = POINT1[0]
        x1 = POINT1[1]

        POINT2 = [int(self.calForce.get()), int(self.calWeight.get())]
        y2 = POINT2[0]
        x2 = POINT2[1]

        self.forceCalibration = (y2-y1)/(x2-x1)

        print('Setting calibration...')

    # This function will move the stage
    def moveStage(self, direction):

        # NEED TO ADD CONVERSION FROM/TO mm HERE. WHAT V = WHAT mm?
        self.setVoltage(direction)
        time.sleep(0.001)
        # NEED TO ADD CONVERSION FROM/TO mm HERE. WHAT V = WHAT mm?
        self.setVoltage(0)
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

    def setLJTick(self):
        dioPin = 4
        # Configure FIO0 to FIO4 as analog inputs, and FIO04 to FIO7 as digital I/O.
        self.U3device.configIO(FIOAnalog=0x0F)
        self.DACnumbers = {'DACA': 48,
                               'DACB': 49}

        EEPROM_ADDRESS = 0x50
        self.sclPin = dioPin
        self.sdaPin = self.sclPin + 1

        data = self.U3device.i2c(EEPROM_ADDRESS, [64],
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

        self.setVoltage(0, 'DACA')
        self.setVoltage(0, 'DACB')


    def setVoltage(self, value):
        pass
        # DAC_ADDRESS = 0x12
        # binaryA = int(value*self.slopeA + self.offsetA)
        # self.U3device.i2c(DAC_ADDRESS,
        #                 [self.DACnumbers[DACPORT], binaryA // 256, binaryA % 256],
        #                 SDAPinNum=self.sdaPin, SCLPinNum=self.sclPin)

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
