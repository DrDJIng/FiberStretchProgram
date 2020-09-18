x = csvread('F:\Guth data\17092020 3.csv');

time = x(:, 1)
force = x(:, 2)
length = x(:, 3)
signal = x(:, 4)

figure(6)
plot(time, force)
