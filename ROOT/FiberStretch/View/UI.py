from tkinter import *
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import ( FigureCanvasTkAgg, NavigationToolbar2Tk )
from matplotlib.backend_bases import key_press_handler
from .buttonFuncs import ButtonFunctions as BF

class MainUI:

    # Define the initialisation, which will initiate all GUI elements
    def __init__(self):
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
        self.signalButton = ttk.Button(self.signalFrame, text = 'Send signal', command = BF.signalButton)
        self.signalButton.grid(column = 2, row = 0)
        self.startButton = ttk.Button(self.signalFrame, text = 'Start measuring', command = lambda : BF.startButton(self))
        self.startButton.grid(column = 2, row = 1, pady = 10)
        self.stopButton = ttk.Button(self.signalFrame, text = 'Stop measuring', command = lambda : BF.stopButton(self))
        self.stopButton.grid(column = 2, row = 2, pady = 10)

        # Stage buttons
        self.stageFrame = ttk.Frame(self.settingsFrame)
        self.stageFrame.grid(column = 1, row = 0)
        self.stageForwardButton = ttk.Button(self.stageFrame, text = 'Stage forward', command = BF.stageMovement)
        self.stageForwardButton.grid(column = 1, row = 2)
        self.stageBackwardButton = ttk.Button(self.stageFrame, text = 'Stage back', command = BF.stageMovement)
        self.stageBackwardButton.grid(column = 2, row = 2)

        # Other buttons
        self.otherFrame = ttk.Frame(self.settingsFrame)
        self.otherFrame.grid(column = 2, row = 0)
        self.exportButton = ttk.Button(self.otherFrame, text = 'Export data', command = BF.saveData)
        self.exportButton.grid(column = 3, row = 0, pady = 10)
        self.calibrateButton = ttk.Button(self.otherFrame, text = 'Calibrate', command = BF.calibrate)
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
        self.root.mainloop()
        return self

if __name__ == '__main__':
    MainUI()
