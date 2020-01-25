import tkinter
import serial
import threading
import time
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt


   
ser = serial.Serial()
com_port = 'com3'
baud_rate = 115200
steps = 30
timer = 24383
data_ADC = list()
degree = list()
thread_flag = False
motorState = {"INACTIVE": 0, "ACTIVE_R": 1, "ACTIVE_L": 2}
currentMotorState = motorState["INACTIVE"]
stop = False


def serial_port_init():
    """
    Initialization of serial port
    """

    ser.port = com_port
    ser.baudrate = baud_rate
    ser.timeout = 0.8
    ser.write_timeout=0.1

    print('Baud Rate =',baud_rate)
    print('Com Port =',com_port)


def convertToVoltage(data):
    """ Convertation ADC data to voltage """
    
    MAX_ADC_DATA = 1023
    MAX_VOLTAGE = 5

    convertData = float((data / MAX_ADC_DATA) * MAX_VOLTAGE )
    
    return convertData
    

def threadRightRotation():
    """ It is called by thread. Starting of the step motor rotation to the
    right. It writes '1' to the com port """

    global currentMotorState
    global motorState
    cmd = b'1'
    
    if ser.isOpen() is False:
        ser.open()

    ser.readline()
    ser.write(cmd)
    currentMotorState = motorState["ACTIVE_R"]


def threadStop():
    """ It is called by thread. Stop of the step motor. It writes '0' to the
    com port """

    global currentMotorState
    global motorState
    cmd = b'0'

    if ser.isOpen() is False:
        ser.open()

    ser.readline()
    ser.write(cmd)
    currentMotorState = motorState["INACTIVE"]   
    

def threadLeftRotation():
    """ It is called by thread. Starting of the step motor rotation to the
    left. It writes '2' to the com port """

    global currentMotorState
    global motorState
    cmd = b'2'
    
    if ser.isOpen() is False:
        ser.open()

    ser.readline()
    ser.write(cmd)
    currentMotorState = motorState["ACTIVE_L"]

def treadDataProcessing():
    """ It is called by thread. It reads data from com port and writes them into data_ADC buffer"""
        
    global data_ADC
    global degree
    global stop
    global thread_flag

    number = 0
    MAX_NUM = 185
            
    while stop is False and number <= MAX_NUM and ser.isOpen() is True:
        ser.flushInput()
        try:
            data = ser.readline()
        except serial.SerialException:
            print("Serial port is not open")
        except serial.serialutil.SerialException:
            print("Serial port is not open")
        except AttributeError:
            print("Invalid data")
        else:    
            if data != b'\n' and data != b'\0' and data != b'':
                try:
                    data = data.decode('ascii')
                    data = int(data)

                    data = convertToVoltage(data)
                except ValueError:
                    print("Incorrect input data")
                except TypeError:
                    print("Incorrect input data")    
                else:
                    data_ADC.append(data)       
                    degree.append(number)
                    number += 1

    thread_flag = False
    data_ADC = []
    degree = []

# Creating class SetupBar
class SetupBar(tkinter.Frame):
    def __init__(self, parent=None):
        tkinter.Frame.__init__(self, parent)
        self.init_window()
    def fetch_baud_rate(self):
        global baud_rate
        baud_rate = self.ent1.get()
        serial_port_init()

    def fetch_com_port(self):
        global com_port
        com_port = self.ent2.get()
        serial_port_init()

    def init_window(self):     
            
        self.label1 = tkinter.Label(self, text= 'Baud Rate:')
        self.label1.grid(column = 0, row = 0, sticky=tkinter.E)
        self.ent1 = tkinter.Entry(self)
        self.ent1.grid(column = 1, row = 0)
        self.ent1.insert(0, baud_rate)
        self.UpdateBaudRate = tkinter.Button(self, text="Update Baud Rate", command=self.fetch_baud_rate)
        self.UpdateBaudRate.grid(column = 1, row = 1, sticky=tkinter.W)

        self.label2 = tkinter.Label(self, text= 'Serial Port:')
        self.label2.grid(column = 0, row = 2, sticky=tkinter.E)
        self.ent2 = tkinter.Entry(self)
        self.ent2.insert(0, com_port) 
        self.ent2.grid(column = 1, row = 2)
        self.UpdateSerialPort = tkinter.Button(self, text="Update Serial Port", command=self.fetch_com_port)
        self.UpdateSerialPort.grid(column = 1, row = 3, sticky=tkinter.W)

        self.label3 = tkinter.Label(self, text= 'Steps:')
        self.label3.grid(column = 0, row = 4, sticky=tkinter.E)
        self.ent3 = tkinter.Entry(self)
        self.ent3.insert(0, steps) 
        self.ent3.grid(column = 1, row = 4)
        self.UpdateSteps = tkinter.Button(self, text="    Update Steps    ")
        self.UpdateSteps.grid(column = 1, row = 5, sticky=tkinter.W)

        self.label4 = tkinter.Label(self, text= 'Time:')
        self.label4.grid(column = 0, row = 6, sticky=tkinter.E)
        self.ent4 = tkinter.Entry(self)
        self.ent4.insert(0, timer) 
        self.ent4.grid(column = 1, row = 6)
        self.UpdateTime = tkinter.Button(self, text="    Update Time    ")
        self.UpdateTime.grid(column = 1, row = 7, sticky=tkinter.W)
   
   
# Here, we are creating our class, WorkSpace, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class WorkSpace(tkinter.Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, parent):
        
        # parameters that you want to send through the Frame class. 
        tkinter.Frame.__init__(self, parent)   

        #reference to the master widget, which is the tk window                 
        self.parent = parent

        #plot instanses
        self.fig, self.ax = plt.subplots()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)  # A tk.DrawingArea.
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent)
        self.toolbar.pack(side=tkinter.BOTTOM)

        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    def init_window(self):
        """ This method creates content of the window"""

        self.menu = tkinter.Menu(self.master)
        self.parent.config(menu=self.menu)

        # create the file object)
        self.file = tkinter.Menu(self.menu)
        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        self.file.add_command(label="Exit", command=self.client_exit)
        #added "file" to our menu
        self.menu.add_cascade(label="File", menu=self.file)

        # changing the title of our master widget      
        self.master.title("Graphic Interface for Antenna Pattern Recorder")
        self.master.iconbitmap('clienticon.ico')

        # allowing the widget to take the full space of the root window
        #self.pack(fill=tkinter.BOTH, expand=1)

        self.plot()

        #self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        #self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # creating a button instances
        self.button_quit = tkinter.Button(master=self.parent, text="Quit", command=self._quit)
        self.button_quit.pack(side=tkinter.RIGHT)

        self.button_read_data = tkinter.Button(master=self.parent, text="Plot", command=self.dataProcessing)
        self.button_read_data.pack(side=tkinter.RIGHT)

        self.button_clear = tkinter.Button(master=self.parent, text="Clear", command=self.clear)
        self.button_clear.pack(side=tkinter.RIGHT)

        self.leftRotation = tkinter.Button(master=self.parent, text="Left Rotation", command=self.leftRotation)
        self.leftRotation.pack(side=tkinter.LEFT, padx=0)

        self.button_stop = tkinter.Button(master=self.parent, text="Stop", command=self.stop)
        self.button_stop.pack(side=tkinter.LEFT)
        #self.button_stop.place(x=600,y=600)

        self.button_rightRotation = tkinter.Button(master=self.parent, text="Right Rotation", command=self.rightRotation)
        self.button_rightRotation.pack(side=tkinter.LEFT)

        self.button_start = tkinter.Button(master=self.parent, text="Start record pattern", command=self.start_record)
        self.button_start.pack(side=tkinter.LEFT)

    def start_record(self):
        self.leftRotation()
        
    def plot(self):
        """ This method is intended for drawing of the plot"""
        
        global degree
        global data_ADC
        global thread_flag
        global stop
        global motor_state

        number = len(data_ADC)

        self.ax.set(xlabel='Degree', ylabel='Voltage', title='Antenna Pattern')
        self.ax.set_xlim(left = 0, right = 180)
        self.ax.set_ylim(bottom = 0, top = 5.5)
        self.ax.plot(degree, data_ADC)
        self.ax.grid()
        self.canvas.draw()
        self.toolbar.update()
   
        if thread_flag is True and stop is False and number <= 180:
            self.parent.after(10, self.plot) # It is timer. Timer expires every 10 ms and after that calls self.plot()
            self.ax.clear()
        else:
            self.parent.after_cancel(self.plot)

    def clear(self):
        """ This method is intended for reseting of the plot"""

        global degree
        global data_ADC
        global thread_flag
        
        self.ax.clear()
        self.ax.set(xlabel='Degree', ylabel='Voltage', title='Antenna Pattern')
        self.ax.set_xlim(left = 0, right = 180)
        self.ax.set_ylim(bottom = 0, top = 5.5)
        self.ax.grid()
        self.canvas.draw()
        self.toolbar.update()

        if stop is True or thread_flag is False:
            data_ADC = []
            degree = []

    def leftRotation(self):
        """ This method creates and launches thread which calls threadLeftRotation()
            for left rotation of the motor"""

        global stop
        stop = False
        thread_lr = threading.Thread(target=threadLeftRotation,)
        thread_lr.start()      

    def stop(self):
        """ This method creates and launches thread which calls threadStop()
            for stop of the motor"""

        global stop
        stop = True
        thread_s = threading.Thread(target=threadStop,)
        thread_s.start()

    def rightRotation(self):
        """ This function creates and launches thread which calls threadRightRotation()
            for right rotation of the motor"""

        global stop
        stop = False
        thread_rr = threading.Thread(target=threadRightRotation,)
        thread_rr.start()

    def dataProcessing(self):
        """ This method creates and launches thread which calls treadDataProcessing()
            for input data processing"""

        global stop
        global thread_flag
        global motorState
        global currentMotorState

        if (stop is False and thread_flag is False) and \
           (currentMotorState == motorState["ACTIVE_L"] or currentMotorState == motorState["ACTIVE_R"]):
            thread_l = threading.Thread(target=treadDataProcessing,)
            thread_l.start()
            thread_flag = True
            self.plot()

    def _quit(self):
        """Stops motor, closes com port and quits from program"""
        
        cmd = b'0'
        if ser.isOpen() is False:
            ser.open()

        ser.readline()
        ser.write(cmd)
        ser.close()  
        self.master.quit()     # stops mainloop
        self.master.destroy()  # this is necessary on Windows to prevent
                               # Fatal Python Error: PyEval_RestoreThread: NULL tstate    

    def client_exit(self):
        """Stops motor, closes com port and quits from program"""
        
        cmd = b'0'
        if ser.isOpen() is False:
            ser.open()

        ser.readline()
        ser.write(cmd)
        ser.close()
        exit()    
 
def main():
    # root window created. Here, that would be the only window, but
    # you can later have windows within windows.
    serial_port_init()
    root = tkinter.Tk()
    

    #creation of an instance
    app1 = SetupBar(root)
    app1.pack(side=tkinter.LEFT)
    app1.config(relief=tkinter.GROOVE, bd=2)
    
    app2 = WorkSpace(root)
    app2.pack(side=tkinter.LEFT)
    
    #mainloop 
    root.mainloop()

if __name__ == '__main__':
    main()
