from ..Experiment import Experiment
import multiprocessing
class ButtonFunctions:

    def __init__(self):
        # Maybe I should add loading calibration data, configurations, etc here?
        pass

    # Start recording and graphing data in new process. Update at 10Hz, perhaps.  Look into blitting for increased performance.
    def startButton(self):
        print("This will start the stream!")
        streamProcess = multiprocessing.Process(target = Experiment.ExperimentFunctions)
        streamProcess.start()

    # Stop recording and graphing data. Maybe should automatically write to disk as well?
    def stopButton(self):
        print("This will stop the stream!")
        # Experiment.stopRecording()

    # Calibrate and send signal to the motor in new process. Maybe just new thread. Everything is done, of course, in Volts
    # but this needs to translate volts to micrometers, I believe. Will need the calibration from the machine.
    def signalButton(self):
        Experiment.SignalOut()

    # Move the stage backward or forward, -'ve for backwards, +'ve for forwards
    def stageMovement(self):
        Experiment.moveStage()

    # Export data in YAML format? Maybe JSON format? I wonder what the best serialisation scheme is.
    def saveData(self):
        Experiment.outputData()

    # Calibrate the force transducer. Will need an initial file with calibration data embedded.
    def calibrate(self):
        Experiment.setCalibration()

if __name__ == '__main__':
    pass
