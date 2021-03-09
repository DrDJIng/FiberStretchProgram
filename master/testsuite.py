
class Device(object):
    pass


class U3(Device):
    def __init__(self, debug = False, autoOpen = True, **kargs):
        
        pass
        

    def getFeedback(self, *commandlist):

        pass
    
    def getCalibrationData(self):
        
        pass
    
    def voltageToDACBits(self, volts, dacNumber = 0, is16Bits = False):
       
        pass
    
    def configIO(self, TimerCounterPinOffset = None, EnableCounter1 = None, EnableCounter0 = None, NumberOfTimersEnabled = None, FIOAnalog = None, EIOAnalog = None, EnableUART = None):
       
        pass
    
class U6(Device):
    
    def streamConfig(self, NumChannels = 1, ResolutionIndex = 0, SamplesPerPacket = 25, SettlingFactor = 0, InternalStreamClockFrequency = 0, DivideClockBy256 = False, ScanInterval = 1, ChannelNumbers = [0], ChannelOptions = [0], ScanFrequency = None, SampleFrequency = None):
        pass
 
    def streamStart(self):
        pass
    
    def getCalibrationData(self):
        pass
    