import datetime as dt
import tkinter as tk
import tkinter.font as tkFont

import matplotlib.figure as figure
import matplotlib.animation as animation
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



import threading
import time
import math
import board
import busio



#import adafruit_fxos8700
#import adafruit_fxas21002c

from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL

#Temp, Humidity, Pressure Sensor
import adafruit_bme280

#i2c_nxp = board.I2C()
#mag_accel_sensor = adafruit_fxos8700.FXOS8700(i2c_nxp)
#gyro_sensor = adafruit_fxas21002c.FXAS21002C(i2c_nxp)

i2c_ls = board.I2C()  # uses board.SCL and board.SDA
accel_gyro = LSM6DS(i2c_ls,0x6A)
mag_sensor = LIS3MDL(i2c_ls,0x1C)

#I2C address for the temp, humidity and pressure sensor is 0x76
i2c_bme = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bme,0x76)
###############################################################################
# Parameters and global variables

# Parameters
update_interval = 100 # Time (ms) between polling/animation updates
max_elements = 144     # Maximum number of elements to store in plot lists

# Declare global variables
root = None
dfont = None
frame = None
canvas = None
ax1 = None
temp_plot_visible = None


# Global variable to remember various states
fullscreen = False
temp_plot_visible = True
IMU_plot_visible = True
raw_plot_visible = True

###############################################################################
# Functions




# Toggle fullscreen
def toggle_fullscreen(event=None):

    global root
    global fullscreen

    # Toggle between fullscreen and windowed modes
    fullscreen = not fullscreen
    root.attributes('-fullscreen', fullscreen)
    resize(None)   

# Return to windowed mode
def end_fullscreen(event=None):

    global root
    global fullscreen

    # Turn off fullscreen mode
    fullscreen = False
    root.attributes('-fullscreen', False)
    resize(None)

# Automatically resize font size based on window size
def resize(event=None):

    global dfont
    global frame

    # Resize font based on frame height (minimum size of 12)
    # Use negative number for "pixels" instead of "points"
    new_size = -max(12, int((frame.winfo_height() / 30)))
    dfont.configure(size=new_size)

# Toggle the temperature plot
def toggle_temp():

    global canvas
    global ax1
    global temp_plot_visible

    # Toggle plot and axis ticks/label
    temp_plot_visible = not temp_plot_visible
    ax1.get_lines()[0].set_visible(temp_plot_visible)
    ax1.get_yaxis().set_visible(temp_plot_visible)
    canvas.draw()

# Toggle the imu plot
def toggle_IMU():

    global canvas
    global ax2
    global IMU_plot_visible

    # Toggle plot and axis ticks/label
    IMU_plot_visible = not IMU_plot_visible
    ax2.get_lines()[0].set_visible(IMU_plot_visible)
    ax2.get_yaxis().set_visible(IMU_plot_visible)
    canvas.draw()

    # Toggle the raw heading plot
def toggle_raw():

    global canvas
    global ax3
    global raw_plot_visible

    # Toggle plot and axis ticks/label
    raw_plot_visible = not raw_plot_visible
    ax3.get_lines()[0].set_visible(raw_plot_visible)
    ax3.get_yaxis().set_visible(raw_plot_visible)
    canvas.draw()

# This function is called periodically from FuncAnimation
def animate(i, ax1, ax2, ax3, xs, temps, head, temp_c, IMU, IMU_raw,raw):

    # Update data to display temperature and light values
    try:
        new_temp = round(bme280.temperature,2)



        
        #mag_x, mag_y, mag_z = mag_accel_sensor.magnetometer
        #yaw = math.atan2(mag_y,mag_x)
        accel_x, accel_y, accel_z = accel_gyro.acceleration
        gyro_x, gyro_y, gyro_z = accel_gyro.gyro
        mag_x, mag_y, mag_z = mag_sensor.magnetic

        #mag calibration offsets for a SPECIFIC device - yours will be different!!
        mag_cal_x = -9
        mag_cal_y = 7
        mag_cal_z = -69
        


        mag_x = mag_x-mag_cal_x
        mag_y = mag_y-mag_cal_y
        mag_z = mag_z-mag_cal_z
        
        accXnorm = accel_x/math.sqrt(accel_x * accel_x + accel_y * accel_y + accel_z * accel_z)
        accYnorm = accel_y/math.sqrt(accel_x * accel_x + accel_y * accel_y + accel_z * accel_z)

        pitch = math.asin(accXnorm)
        roll = -math.asin(accYnorm/math.cos(pitch))

        yaw = 57.2958*math.atan2(mag_y,mag_x)
        
        magXcomp = mag_x*math.cos(math.asin(accXnorm))+mag_z*math.sin(pitch)
        magYcomp = mag_x*math.sin(math.asin(accYnorm/math.cos(pitch)))*math.sin(math.asin(accXnorm))+mag_y*math.cos(math.asin(accYnorm/math.cos(pitch)))-mag_z*math.sin(math.asin(accYnorm/math.cos(pitch)))*math.cos(math.asin(accXnorm))
        #yaw_tilt = math.atan2(magYcomp,magXcomp);
        #heading = 57.2958*math.atan2(magYcomp,magXcomp)

        x_h = mag_x*math.cos(pitch) + mag_z*math.sin(pitch)
        y_h = mag_x*math.sin(roll) * math.sin(pitch)+ mag_y*math.cos(roll) - mag_z*math.sin(roll) * math.cos(pitch)
        heading = 57.2958*math.atan2(y_h,x_h)
        


        if heading < 0:
            heading += 360;
        if yaw < 0:
            yaw += 360;
        new_IMU = round(heading)
        new_raw = round(yaw)
    except:
        pass

    # Update our labels
    temp_c.set(new_temp)
    IMU.set(new_IMU)
    IMU_raw.set(new_raw)

    # Append timestamp to x-axis list
    timestamp = mdates.date2num(dt.datetime.now())
    xs.append(timestamp)

    # Append sensor data to lists for plotting
    temps.append(new_temp)
    head.append(new_IMU)
    raw.append(new_raw)

    # Limit lists to a set number of elements
    xs = xs[-max_elements:]
    temps = temps[-max_elements:]
    head = head[-max_elements:]
    raw = raw[-max_elements:]

    # Clear, format, and plot light values first (behind)
    color = 'tab:red'
    ax1.clear()
    ax1.set_ylabel('Temperature (C)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.plot(xs, temps, linewidth=2, color=color)

    # Clear, format, and plot temperature values (in front)
    color = 'tab:blue'
    ax2.clear()
    ax2.set_ylabel('Heading (deg)', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.plot(xs, head, linewidth=2, color=color)

    # Clear, format, and plot temperature values (in front)
    color = 'tab:green'
    ax3.clear()
    ax3.set_ylabel('raw (deg)', color=color)
    ax3.tick_params(axis='y', labelcolor=color)
    ax3.plot(xs, raw, linewidth=2, color=color)

    # Format timestamps to be more readable
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate()

    # Make sure plots stay visible or invisible as desired
    ax1.get_lines()[0].set_visible(temp_plot_visible)
    ax2.get_lines()[0].set_visible(IMU_plot_visible)
    ax3.get_lines()[0].set_visible(raw_plot_visible)
# Dummy function prevents segfault
def _destroy(event):
    pass

###############################################################################
# Main script

# Create the main window
root = tk.Tk()
root.title("Sensor Dashboard")

# Create the main container
frame = tk.Frame(root)
frame.configure(bg='white')

# Lay out the main container (expand to fit window)
frame.pack(fill=tk.BOTH, expand=1)

# Create figure for plotting
fig = figure.Figure(figsize=(2, 2))
fig.subplots_adjust(left=0.1, right=0.8)
ax1 = fig.add_subplot(1, 1, 1)

# Instantiate a new set of axes that shares the same x-axis
ax2 = ax1.twinx()

# Instantiate a new set of axes that shares the same x-axis
ax3 = ax2.twiny()

# Empty x and y lists for storing data to plot later
xs = []
temps = []
head = []
raw = []

# Variables for holding data
temp_c = tk.DoubleVar()
IMU = tk.DoubleVar()
IMU_raw = tk.DoubleVar()

# Create dynamic font for text
dfont = tkFont.Font(size=-24)

# Create a Tk Canvas widget out of our figure
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas_plot = canvas.get_tk_widget()

# Create other supporting widgets
label_temp = tk.Label(frame, text='Temp:', font=dfont, bg='white')
label_celsius = tk.Label(frame, textvariable=temp_c, font=dfont, bg='white')
label_unitc = tk.Label(frame, text="C", font=dfont, bg='white')
label_head = tk.Label(frame, text="Head:", font=dfont, bg='white')
label_raw = tk.Label(frame, text="raw:", font=dfont, bg='white')
label_heading = tk.Label(frame, textvariable=IMU, font=dfont, bg='white')
label_unithead = tk.Label(frame, text="deg", font=dfont, bg='white')
button_temp = tk.Button(    frame, 
                            text="Toggle T", 
                            font=dfont,
                            command=toggle_temp)
button_IMU= tk.Button(   frame,
                            text="Toggle IMU",
                            font=dfont,
                            command=toggle_IMU)
button_raw= tk.Button(   frame,
                            text="Toggle raw",
                            font=dfont,
                            command=toggle_raw)
button_quit = tk.Button(    frame,
                            text="Quit",
                            font=dfont,
                            command=root.destroy)

# Lay out widgets in a grid in the frame
canvas_plot.grid(   row=0, 
                    column=0, 
                    rowspan=5, 
                    columnspan=4, 
                    sticky=tk.W+tk.E+tk.N+tk.S)
label_temp.grid(row=0, column=4, columnspan=2)
label_celsius.grid(row=1, column=4, sticky=tk.E)
label_unitc.grid(row=1, column=5, sticky=tk.W)
label_heading.grid(row=2, column=4, columnspan=2)
label_head.grid(row=3, column=4, sticky=tk.E)
label_unithead.grid(row=3, column=5, sticky=tk.W)
button_temp.grid(row=5, column=0, columnspan=2)
button_IMU.grid(row=5, column=2, columnspan=2)
button_raw.grid(row=5, column=3, columnspan=2)
button_quit.grid(row=5, column=4, columnspan=2)

# Add a standard 5 pixel padding to all widgets
for w in frame.winfo_children():
    w.grid(padx=5, pady=5)

# Make it so that the grid cells expand out to fill window
for i in range(0, 5):
    frame.rowconfigure(i, weight=1)
for i in range(0, 5):
    frame.columnconfigure(i, weight=1)

# Bind F11 to toggle fullscreen and ESC to end fullscreen
root.bind('<F11>', toggle_fullscreen)
root.bind('<Escape>', end_fullscreen)

# Have the resize() function be called every time the window is resized
root.bind('<Configure>', resize)

# Call empty _destroy function on exit to prevent segmentation fault
root.bind("<Destroy>", _destroy)

# Call animate() function periodically
fargs = (ax1, ax2, ax3, xs, temps, head, temp_c, IMU, IMU_raw,raw)
ani = animation.FuncAnimation(  fig, 
                                animate, 
                                fargs=fargs, 
                                interval=update_interval)               

# Start in fullscreen mode and run
toggle_fullscreen()
root.mainloop()
