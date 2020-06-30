from FiberStretch.View.UI import MainUI
from FiberStretch.Controller import LabJackPython
from FiberStretch.Controller import u3 as u3
from FiberStretch.Controller import u6 as u6
import queue as Queue

class FiberStretchProgram:

    def __init__(self):
        self.data = 1
        # Initialised
        # load calibration data, options, etc. Pass into MainUI.
        MainUI()

if __name__ == '__main__':
    FiberStretchProgram()
