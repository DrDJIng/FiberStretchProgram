from FiberStretch.Controller import LabJackPython
from FiberStretch.Controller import u6 as u6

class ExperimentFunctions:
    def __init__(self):
        self.startRecording()

    # Set up the LabJack and start the streaming process
    def startRecording(self):
        self.device = u6.U6()
        # For applying the proper calibration to readings.
        self.device.getCalibrationData()

        print('Starting data stream...')

        print("Configuring U6 stream")

        # Set scan frequency to 2x double what we want actual frequency to be at. Could probably do this non-stream,
        # but two channels at 100Hz feels like a streaming problem to me.  Attach to an editable field at some point.
        SCAN_FREQUENCY = 200
        MAX_REQUESTS = 10
        self.finished = False

        # Set up the stream from Labjack U6
        self.device.streamConfig(NumChannels=2, ChannelNumbers=[0, 1], ChannelOptions=[0, 0], SettlingFactor=1, ResolutionIndex=3, ScanFrequency=SCAN_FREQUENCY)
        while not self.finished:
            self.device.streamStart()
            missed = 0
            dataCount = 0
            packetCount = 0

            for r in self.device.streamData():
                # Update y-axis data to plot, auto-axis should keep it within range
                updateData = r["AIN0"]
                # Append onto all data, for export later
                # self.forceData = self.forceData + r["AIN0"]
                # self.lengthData = self.lengthData + r["AIN1"]

                dataCount += 1
                print(len(updateData))

                # Our stop condition
            if self.dataCount >= MAX_REQUESTS:
                self.finished = True

        self.device.streamStop()
        print("Stream stopped.\n")
        return
