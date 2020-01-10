import serial
import time
ser = serial.Serial('COM5', 9600)
time.sleep(2)
ser.write(b'1')                # change from 1 to 2 to rotate at both sides
# Read and record the data
data =[]                       # empty list to store the data
for i in range(155):           # number of degrees
    b = ser.readline()         # read a byte string
    string_n = b.decode()  # decode byte string into Unicode  
    string = string_n.rstrip() # remove \n and \r
    flt = float(string)        # convert string to float
    print(flt)
    data.append(flt)           # add to the end of data list
   
ser.close()
# show the data

for line in data:
    print(line)

    import matplotlib.pyplot as plt
# if using a Jupyter notebook include %matplotlib inline

plt.plot(data)
plt.xlabel('Degrees')
plt.ylabel('Data Reading')
plt.title('Data Reading vs. Degrees')
plt.show()
