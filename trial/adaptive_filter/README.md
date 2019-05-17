# adaptive-filter

Development of an adaptive filter to cancel out mechanical interference on an optical signal, using information about the interference contained in accelerometer-data.


One of our optical sensors has been running statically (no movement) in our laboratory.
The sensor has been hit with steel bars and plastic hammers to simulate heavy mechanical interferences on the sensor’s optics which can happen in some of our customer’s industrial environments (e.g. drill hammer). The electronics of the sensor at hand have therefore been equipped with an additional side-channel sensor (3-axis accelerometer).

The dataset for this task contains the 3 axes of the acceleration sensor as well as an analog signal stream from our optical measurement system inside the sensor. Your goal in this exercise is to find a model which makes use of the degree of information about the mechanical interference in the accelerometer-data in order to cancel out the interference on the optical signal.


SOLUTION

For each of this signal, do the three following steps:

1) generate a new signal qF, given by the linear combination of the three accelerometer signals. The coefficients of the linear combinations are found by maximising the correlation between qF and the optical signal qV;

2) apply an adaptive filter using qV and qF, using a FIR filter with LMS;

3) compute the residual interference. This is done by computing the average power of the original optical signal qV and of the error signal (i.e. qV where interference has been canceled), and by considering the inverse of SNR.
