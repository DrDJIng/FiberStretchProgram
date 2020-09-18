using CSV
using GR, Interact
data = CSV.read("F:\\Guth data\\17092020 12.csv")
timedata = data[:, 1]
force = data[:, 2]
length = data[:, 3]
signal = data[:, 4]

t = plot(timedata, force)
gui()
plot(timedata, length)
plot(timedata, signal)
