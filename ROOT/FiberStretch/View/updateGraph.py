def updateGraph(self):
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
