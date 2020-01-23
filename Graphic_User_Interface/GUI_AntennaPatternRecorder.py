import tkinter
import time
import serial

ser = serial.Serial()
com_port = 'com4'
baud_rate = 9600
steps = 30
timer = 24383

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
   
def serial_port_init():
    """
    Initialization of serial port
    """

    ser.port = com_port
    ser.baudrate = baud_rate
    ser.timeout = 2

    print('Baud Rate =',baud_rate)
    print('Com Port =',com_port)

data_ADC = list()
degree = list()
motor_state = False


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
    def __init__(self, parent=None):
        
        # parameters that you want to send through the Frame class. 
        tkinter.Frame.__init__(self, parent)   

        #reference to the master widget, which is the tk window                 
        #self.master = master

        #plot instanses
        self.fig, self.ax = plt.subplots()

        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window()

    #Creation of init_window
    def init_window(self):

        self.menu = tkinter.Menu(self.master)
        self.master.config(menu=self.menu)

        # create the file object)
        self.file = tkinter.Menu(self.menu)
        # adds a command to the menu option, calling it exit, and the
        # command it runs on event is client_exit
        self.file.add_command(label="Exit", command=self.client_exit)
        #added "file" to our menu
        self.menu.add_cascade(label="File", menu=self.file)

        # changing the title of our master widget      
        self.master.title("Graphic Interface for Antenna Pattern Recorder")

        # allowing the widget to take the full space of the root window
        #self.pack(fill=tkinter.BOTH, expand=1)

        self.plot()

        self.canvas = FigureCanvasTkAgg(self.fig, self)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # creating a button instances
        self.button_quit = tkinter.Button(self, text="Quit", command=self._quit)
        self.button_quit.pack(side=tkinter.RIGHT)

        self.button_read_data = tkinter.Button(self, text="Plot", command=self.read_data)
        self.button_read_data.pack(side=tkinter.RIGHT)

        self.button_clear = tkinter.Button(self, text="Clear", command=self.clear)
        self.button_clear.pack(side=tkinter.RIGHT)

        self.leftRotation = tkinter.Button(self, text="Left Rotation", command=self.leftRotation)
        self.leftRotation.pack(side=tkinter.LEFT)

        self.button_stop = tkinter.Button(self, text="Stop", command=self.stop)
        self.button_stop.pack(side=tkinter.LEFT)

        self.button_rightRotation = tkinter.Button(self, text="Right Rotation", command=self.rightRotation)
        self.button_rightRotation.pack(side=tkinter.LEFT)

        self.button_start = tkinter.Button(self, text="Start record pattern", command=self.start_record)
        self.button_start.pack(side=tkinter.LEFT)

    def start_record(self):
        self.leftRotation()
        
    def plot(self):
        self.ax.clear()
        self.ax.set(xlabel='Numers', ylabel='ADC data', title='Antenna Pattern')
        self.ax.set_xlim(left = 0, right = 180)
        self.ax.set_ylim(bottom = 0, top = 1100)
        self.ax.plot(degree, data_ADC)
        self.ax.grid()

    def clear(self):
        self.ax.clear()
        self.ax.set(xlabel='Numers', ylabel='ADC data', title='Antenna Pattern')
        self.ax.set_xlim(left = 0, right = 180)
        self.ax.set_ylim(bottom = 0, top = 1100)
        self.ax.grid()
        self.canvas.draw()
        self.toolbar.update()

    def leftRotation(self):
        """
        Starting of the step motor rotation to the left.
        It writes '2' to the com port
        """

        global motor_state
        cmd = b'2'
        try:
            ser.open()
        except serial.SerialException:
            ser.close()
            ser.open()
        finally:
            ser.readline()
            ser.write(cmd)

        motor_state = True      

    def stop(self):
        """
        Stop of the step motor.
        It writes '0' to the com port
        """

        global motor_state
        cmd = b'0'
        try:
            ser.open()
        except serial.SerialException:
            ser.close()
            ser.open()
        finally:
            ser.readline()
            ser.write(cmd)

        motor_state = False

    def rightRotation(self):
        """
        Starting of the step motor rotation to the right.
        It writes '1' to the com port
        """

        global motor_state
        cmd = b'1'
        try:
            ser.open()
        except serial.SerialException:
            ser.close()
            ser.open()
        finally:
            ser.readline()
            ser.write(cmd)

        motor_state = True

    def read_data(self):

        global data_ADC
        global degree
        global motor_state
        number = 0

        while motor_state is True and number <= 180:

            data = str(ser.readline())
            idx = data.find("\\n")
            data = int(data[2:idx])
            print (data)
            data_ADC.append(data)       
            degree.append(number)
            number += 1        

            self.plot() 
            self.canvas.draw()
            self.toolbar.update()

        data_ADC = []
        degree = []

    def _quit(self):
        cmd = b'0'
        try:
            ser.open()
        except serial.SerialException:
            ser.close()
            ser.open()
        finally:
            ser.readline()
            ser.write(cmd)
            ser.close()
        self.master.quit()     # stops mainloop
        self.master.destroy()  # this is necessary on Windows to prevent
                               # Fatal Python Error: PyEval_RestoreThread: NULL tstate    

    def client_exit(self):
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
