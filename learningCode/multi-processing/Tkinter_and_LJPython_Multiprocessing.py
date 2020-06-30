import multiprocessing as mp
import u3
import time
import tkinter as tk

# LabJack IO
loadcell_chan = 6
accel_ref_chan = 4
accel_x_chan = 5

LJ_IO_config = 112


class Idle(tk.Tk):

    def __init__(self, *args, **kwargs):  # Allow input of args and kwargs for future use

        # Initialize the application

        tk.Tk.__init__(self, *args, **kwargs)
        self.idle()

    def idle(self):

        while(True):
            time.sleep(1)
            print('success!')


class GrabSomeData:

    def __init__(self):
    # Set-up LabJack
        self.daq = u3.U3()
        self.daq.getCalibrationData()

        self.daq.configIO(FIOAnalog=LJ_IO_config)

        # Setup loadcell input
        self.daq.getFeedback(
            u3.AIN(PositiveChannel=loadcell_chan, NegativeChannel=31, LongSettling=False, QuickSample=False))

        # Setup accelerometer input
        self.daq.getFeedback(
            u3.AIN(PositiveChannel=accel_ref_chan, NegativeChannel=31, LongSettling=False, QuickSample=False))
        self.daq.getFeedback(
            u3.AIN(PositiveChannel=accel_x_chan, NegativeChannel=31, LongSettling=False, QuickSample=False))
        self.print_data()

    def print_data(self):

        while(True):
            # Read in the loadcell, accelerometer and encoder data.

            loadcell_v = self.daq.getAIN(6)
            accelerometer_ref = self.daq.getAIN(4, 32)
            accelerometer_v = self.daq.getAIN(5, 32)

            print('success!' + str(loadcell_v))
            time.sleep(1)


if __name__ == "__main__":

    # create the backend data process
    BTABackends = mp.Process(target=GrabSomeData)
    BTABackends.daemon = True
    BTABackends.name = 'TesterBackend'
    BTABackends.start()

    sit_here = Idle()
    sit_here.mainloop()
