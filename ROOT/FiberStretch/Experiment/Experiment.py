class Experiment:

# Set up the LabJack and start the streaming process
  def startRecordings(self, device):
      global shouldPlotContinue
      global streamStopper
      streamStopper = 0 # To stop the streaming/thread.
      shouldPlotContinue = 1 # Graphs should update.

      self.device = device

      print('Starting data stream...')

      print("Configuring U6 stream")

      # Set scan frequency to 2x double what we want actual frequency to be at. Could probably do this non-stream, but two channels at 100Hz feels like a streaming problem to me.  Attach to an editable field at some point.
      SCAN_FREQUENCY = 200

      # Set up the stream from Labjack U6
      self.device.streamConfig(NumChannels=2, ChannelNumbers=[0, 1], ChannelOptions=[0, 0], SettlingFactor=1, ResolutionIndex=3, ScanFrequency=SCAN_FREQUENCY)
      while streamStopper == 0:
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
                  if streamStopper == 1:
                      break

                  if r["errors"] != 0:
                      print("Errors counted: %s ; %s" % (r["errors"], datetime.now()))

                  if r["numPackets"] != self.device.packetsPerRequest:
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

      self.device.streamStop()
      print("Stream stopped.\n")
      return
