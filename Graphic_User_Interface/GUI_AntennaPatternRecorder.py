import tkinter
import serial

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import matplotlib.pyplot as plt
   

ser = serial.Serial(port = 'com3', baudrate = 9600, timeout = 1)

data_ADC = list()
degree = list()
motor_state = False
    

# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class Window(tkinter.Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):
        
        # parameters that you want to send through the Frame class. 
        tkinter.Frame.__init__(self, master)   

        #reference to the master widget, which is the tk window                 
        self.master = master

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

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # creating a button instances
        self.button_quit = tkinter.Button(master=self.master, text="Quit", command=self._quit)
        self.button_quit.pack(side=tkinter.RIGHT)

        self.button_read_data = tkinter.Button(master=self.master, text="Plot", command=self.read_data)
        self.button_read_data.pack(side=tkinter.RIGHT)

        self.button_clear = tkinter.Button(master=self.master, text="Clear", command=self.clear)
        self.button_clear.pack(side=tkinter.RIGHT)

        self.leftRotation = tkinter.Button(master=self.master, text="Left Rotation", command=self.leftRotation)
        self.leftRotation.pack(side=tkinter.LEFT)

        self.button_stop = tkinter.Button(master=self.master, text="Stop", command=self.stop)
        self.button_stop.pack(side=tkinter.LEFT)

        self.button_rightRotation = tkinter.Button(master=self.master, text="Right Rotation", command=self.rightRotation)
        self.button_rightRotation.pack(side=tkinter.LEFT)


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
    root = tkinter.Tk()

    #root.geometry("400x300")

    #creation of an instance
    app = Window(root)

    #mainloop 
    root.mainloop()

if __name__ == '__main__':
    main()
    

