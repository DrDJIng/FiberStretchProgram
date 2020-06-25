import u6

d = u6.U6()

# For applying the proper calibration to readings.
d.getCalibrationData()

DAC0_VALUE = d.voltageToDACBits(1.5, dacNumber = 0, is16Bits = False)
d.getFeedback(u6.DAC0_8(DAC0_VALUE))