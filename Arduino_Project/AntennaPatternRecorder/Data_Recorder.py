import serial
import time

# Set motor at zero degree point
ser = serial.Serial('COM5', 9600)
time.sleep(2)
ser.write(b'1')
ser.close()

# Rotate motor to the end
ser = serial.Serial('COM5', 9600)
time.sleep(2)
ser.write(b'2')

# Read and record the data
data =[]                       # empty list to store the data
for i in range(155):           # number of degrees
    b = ser.readline()         # read a byte string
    string_n = b.decode()      # decode byte string into Unicode
    string = string_n.rstrip() # remove \n and \r
    flt = float(string)        # convert string to float
    print(flt)
    data.append(flt)           # add to the end of data list
ser.close()

# Set motor at zero degree point 
ser = serial.Serial('COM5', 9600)
time.sleep(2)
ser.write(b'1')
ser.close()

# Save data in file
with open('data.txt', 'w') as filehandle:
    filehandle.writelines("%.1f\n" % place for place in data)

# show the data
for line in data:
    print(line)
    import matplotlib.pyplot as plt
plt.plot(data)
plt.xlabel('Degrees')
plt.ylabel('Data Reading')
plt.title('Data Reading vs. Degrees')
plt.show()
