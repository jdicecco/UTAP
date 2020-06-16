import threading
import time
import math
import board
import busio
import adafruit_bno055
import adafruit_ssd1306
import adafruit_pca9685
import adafruit_bme280
from PIL import Image, ImageDraw, ImageFont
import digitalio
#import spidev

import os, sys, struct, array
from fcntl import ioctl
import RPi.GPIO as GPIO

import subprocess

#I2C address for the PWM driver board retrieved automatically
i2c_pwm = board.I2C()
pwm = adafruit_pca9685.PCA9685(i2c_pwm)

   
pwm.frequency = 1600
#I2C address for the IMU is 0x28
i2c_bno = board.I2C()
sensor = adafruit_bno055.BNO055_I2C(i2c_bno,0x28)

#I2C address for the OLED screen is 0x3c
i2c_oled = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128,64, i2c_oled,addr=0x3c,reset=[])

# spi = busio.SPI(board.SCK, MOSI=board.MOSI)
# reset_pin = digitalio.DigitalInOut(board.D4) # any pin!
# cs_pin = digitalio.DigitalInOut(board.D5)    # any pin!
# dc_pin = digitalio.DigitalInOut(board.D6)    # any pin!
# WIDTH = 128
# HEIGHT = 64  # Change to 64 if needed
# BORDER = 5

#oled = adafruit_ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, dc_pin, reset_pin, cs_pin)

#I2C address for the temp, humidity and pressure sensor is 0x76
i2c_bme = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bme,0x76)

xx = 0
yy = 0

rollDeg = 0           
pitchDeg = 0
yawDeg = 0
yawE = 0
pitchE = 0
yaw = 0
pi = 3.1415926

prevYaw = 0
prevPitch = 0
prevRoll = 0

def sensor_read(arg1):
    while True:
        global yy
        global xx

        global yaw
        global pitch
        global roll
        
        global yawDeg
        global yawE
        global pitchDeg
        global rollDeg
        
        #take 10 readings per second
        time.sleep(0.1)        
        w = (sensor.quaternion[0])
        x = (sensor.quaternion[1])
        y = (sensor.quaternion[2])
        z = (sensor.quaternion[3])
        pitch = 0
        yaw = 0
        roll = 0
        try:
         #if (isinstance(w,float) and isinstance(x,float) and isinstance(y,float) and isinstance(z,float)):  
            #print("The quat: {} ".format(sensor.quaternion))
            yaw = (math.atan2(2*(w*z+x*y),1-2*(y*y+z*z)))
            pitch = (math.asin(2*w*y - z*y))
            roll = (math.atan2(2*(w*x+y*z),1-2*(x*x+y*y)))
            yawE = sensor.euler[0]
            pitchE = sensor.euler[1]
            prevYaw = yaw
            prevPitch = pitch
            prevRoll = roll
        except:
            pitch = prevPitch
            yaw = prevYaw
            roll = prevRoll
            yawE = 0
            pitchE = 0
        #convert radians to degrees
        rollDeg = -roll*57.2958            
        pitchDeg = -pitch*57.2958
        yawDeg = -yaw*57.2958
        #print("Yaw: {}".format(sensor.euler[0]))
        #print("Yaw2: {}".format(yawDeg))
        #print("Pitch: {}".format(sensor.euler[1]))
        #print("Pitch2: {}".format(pitchDeg))
        #print("cal: {}".format(sensor.calibration_status))
        #line (radius) in compass is 23 pixels (compass is 46 pixels wide)
        #offset by pi to orient the display so top is north
        xx = round(math.sin(yaw+pi)*23)
        yy = round(math.cos(yaw+pi)*23)
        
        image = Image.new("1",(128,64))
        draw = ImageDraw.Draw(image)
        
        font = ImageFont.load_default()

        draw.ellipse((41,17,87,63),outline=255, fill=0)#left,top,right,bottom
             
        draw.line((xx+64,yy+41,64,41),fill=255) #[left (beginning), top] head, [right (end), bottom] tail - tail is always at center

        draw.text((0,-2),"Yaw: {}".format(round(yawDeg)),font=font,fill=255)
        draw.text((64,-2),"Pitch: {}".format(round(pitchDeg)),font=font,fill=255)
        draw.text((0,6),"Roll: {}".format(round(rollDeg)),font=font,fill=255)

        draw.text((0,14),"T: {:0.1f}C".format((bme280.temperature)),font=font,fill=255)
        draw.text((0,22),"H: {}%".format(round(bme280.humidity)),font=font,fill=255)
        draw.text((64,6),"P: {}mbar".format(round(bme280.pressure)),font=font,fill=255)
        
        draw.text((80,14),"PchE: {}".format(round(pitchE)),font=font,fill=255)

        
        draw.text((80,55),"YawE:{}".format(round(yawE)),font=font,fill=255)  
        draw.text((0,55),"c:{}".format(sensor.calibration_status[0]),font=font,fill=255)  
        draw.text((20,55),"{}".format(sensor.calibration_status[1]),font=font,fill=255)  
        draw.text((29,55),"{}".format(sensor.calibration_status[2]),font=font,fill=255)
        draw.text((39,55),"{}".format(sensor.calibration_status[3]),font=font,fill=255)
        oled.image(image)
        oled.show()
        
t = threading.Thread(target=sensor_read,args=(1,), daemon=True).start()

# Create blank image for drawing.
oled.fill(0)
oled.show()

# Setup OLED screen - get parameters
width = oled.width
height = oled.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image. 0,0 is the upper left pixel
draw.rectangle((0,0,width,height), outline=0, fill=0)
font = ImageFont.load_default()


#### CONFIGURE THE RPI TO INTERFACE WITH CONTROL BOARD ####

#Make it easier to remember which pins control which motors
GR1 = 19
GR2 = 21
BL1 = 13 
BL2 = 17
OR1 = 20
BR1 = 27


#Do the same for the corresponding PWM signals
GR1_PWM = 1
GR2_PWM = 5
BL1_PWM = 3
BL2_PWM = 7
OR1_PWM = 0
BR1_PWM = 2


#Use the numbering scheme for the Broadcom chip, not the RPi pin numbers
GPIO.setmode(GPIO.BCM)

#Turn off warnings about pins being already configured
GPIO.setwarnings(False) 


#Setup pins to control direction on the motor driver chip (MAXIM's MAX14870)
GPIO.setup(GR1,GPIO.OUT)#Green 1
GPIO.setup(GR2,GPIO.OUT)#Green 2
GPIO.setup(BL1,GPIO.OUT)#Blue 1
GPIO.setup(BL2,GPIO.OUT)#Blue 2
GPIO.setup(OR1,GPIO.OUT)#Orange 1
GPIO.setup(BR1,GPIO.OUT)#Brown 1


#status LEDs
GPIO.setup(6,GPIO.OUT)#
GPIO.setup(16,GPIO.OUT)#


# Based on code released by rdb under the Unlicense (unlicense.org)
# Based on information from:
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt

# Find the joystick device(s)
print('Available devices:')

#need to check to make sure a joystick has been connected before we proceed
#if not, we'll just wait here until someone connects a joystick

#this is usually called a flag and is used to check a condition
#when the desired condition is met, we change the value of the flag
joy_not_found = 1

while joy_not_found:
    for fn in os.listdir('/dev/input'):
            if fn.startswith('js'):
                print('  /dev/input/%s' % (fn))
            joy_not_found = 0


# We'll store the states of the axes and buttons
axis_states = {}
button_states = {}

# These constants were borrowed and modified from linux/input.h
axis_names = {
    0x00 : 'x',
    0x01 : 'y',
    0x02 : 'rx',
    0x03 : 'x2',
    0x04 : 'y2',
    0x05 : 'ry',
    0x10 : 'hat0x',
    0x11 : 'hat0y',
}

button_names = {
    0x130 : 'a',
    0x131 : 'b',
    0x133 : 'x',
    0x134 : 'y',
    0x136 : 'LB',
    0x137 : 'RB',
    0x13a : 'select',
    0x13b : 'start',
    0x13c : 'mode',
    0x13d : 'thumbl',
    0x13e : 'thumbr',
}

axis_map = []
button_map = []

# Open the joystick device.
fn = '/dev/input/js0'
print('Opening %s...' % fn)
jsdev = open(fn, 'rb')

# Get the device name.
#buf = bytearray(63)
buf = array.array('B', [0] * 64)
ioctl(jsdev, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
js_name = buf.tobytes().rstrip(b'\x00').decode('utf-8')
print('Device name: %s' % js_name)

# Get number of axes and buttons.
buf = array.array('B', [0])
ioctl(jsdev, 0x80016a11, buf) # JSIOCGAXES
num_axes = buf[0]

buf = array.array('B', [0])
ioctl(jsdev, 0x80016a12, buf) # JSIOCGBUTTONS
num_buttons = buf[0]

# Get the axis map.
buf = array.array('B', [0] * 0x40)
ioctl(jsdev, 0x80406a32, buf) # JSIOCGAXMAP

for axis in buf[:num_axes]:
    axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
    axis_map.append(axis_name)
    axis_states[axis_name] = 0.0

# Get the button map.
buf = array.array('H', [0] * 200)
ioctl(jsdev, 0x80406a34, buf) # JSIOCGBTNMAP

for btn in buf[:num_buttons]:
    btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
    button_map.append(btn_name)
    button_states[btn_name] = 0

print(('%d axes found: %s' % (num_axes, ', '.join(axis_map))))
print(('%d buttons found: %s' % (num_buttons, ', '.join(button_map))))







#Declare variables for use later
#These will be the values from the right joystick
intValx2 = 0
intValy2 = 0

#These will be the values from the left joystick
intValx = 0
intValy = 0

#These will be the values from the two triggers in the front of the joystick
intValrx = 0
intValry = 0

#A TRY-CATCH in programming allows a program to fail gracefully if the "try" portion
#cannot be executed
try:

    # Main event loop
    while True:

        # Joystick code based on release by rdb under the Unlicense (unlicense.org)
        # Based on information from:
        # https://www.kernel.org/doc/Documentation/input/joystick-api.txt
        GPIO.output(16,GPIO.HIGH)#turn on white LED to indicate the program is running

        evbuf = jsdev.read(8)
        if evbuf:
            tyme, value, type, number = struct.unpack('IhBB', evbuf)

        if type & 0x80:
            print("(initial)",end=""),

        if type & 0x01:
            button = button_map[number]
            if button:
                button_states[button] = value
            if value:
                print("%s pressed" % (button))
            else:
                print("%s released" % (button))
            if button == "y":
                GPIO.output(6,GPIO.HIGH)#turn on other LED
            else:
                GPIO.output(6,GPIO.LOW)#otherwise turn it off - should turn off when any other button is pushed
            if button == "b":

                print("Yaw: {}".format(sensor.euler[0]))    
                print("Yaw2: {}".format(yawDeg))
                print("Pitch: {}".format(sensor.euler[1]))
                print("Pitch2: {}".format(pitchDeg))
                print("Roll: {}".format(sensor.euler[2]))
                print("Roll2: {}".format(rollDeg))


            #else:
                #print("Calibration: {}".format(sensor.calibration_status))
        if type & 0x02:
            axis = axis_map[number]
            #right joystick fwd/rev
            if axis=="y2":          
                fvalue = value
                axis_states[axis] = fvalue
                intValy2 = int(fvalue)*2+1
                print("%d" % (intValy2))
            #right joystick left/right
            if axis=="x2":
                fvalue = value
                axis_states[axis] = fvalue
                intValx2 = int(fvalue)*2+1
                    #left joystick fwd/rev      
            if axis=="y":
                fvalue = value
                axis_states[axis] = fvalue
                intValy = int(fvalue)*2+1
            #left joystick left/right
            if axis=="x":
                fvalue = value
                axis_states[axis] = fvalue
                intValx = int(fvalue)*2+1
                    #front right trigger fwd (vehicle ascend)
            if axis=="ry":
                fvalue = value
                axis_states[axis] = fvalue
                intValry = int(fvalue)*2+1
            #front left trigger rev (vehicle descend)
            if axis=="rx":
                fvalue = value
                axis_states[axis] = fvalue
                intValrx = int(fvalue)*2+1
                
                
            #There's a nice tutorial for single joysick control at http://home.kendra.com/mauser/Joystick.html      
            if intValy2<-100:
            

                GPIO.output(GR1,GPIO.LOW)#direction pin
                GPIO.output(GR2,GPIO.LOW)#direction pin
                
                #pwm.setPWM(GR1_PWM,0,abs(intValy2)+1)
                #pwm.setPWM(GR2_PWM,1,abs(intValy2)+1)
                pwm.channels[GR2_PWM].duty_cycle = abs(intValy2)
                
            elif intValy2>100:

                GPIO.output(GR1,GPIO.HIGH)#direction pin
                GPIO.output(GR2,GPIO.HIGH)#direction pin
                    
                #pwm.setPWM(GR1_PWM,0,abs(intValy2)+1)
                pwm.channels[GR2_PWM].duty_cycle = (intValy2)                  
                                
            else:
                pwm.channels[GR1_PWM].duty_cycle = 0 
                pwm.channels[GR2_PWM].duty_cycle = 0

            if intValy>100:
            
                GPIO.output(BL1,GPIO.HIGH)#direction pin
                GPIO.output(BL2,GPIO.HIGH)#direction pin

                #pwm.setPWM(BL1_PWM,0,abs(intValy)+1)
                pwm.channels[BL2_PWM].duty_cycle = (intValy) 

            elif intValy<-100:
            
                GPIO.output(BL1,GPIO.LOW)#direction pin
                GPIO.output(BL2,GPIO.LOW)#direction pin

                #pwm.setPWM(BL1_PWM,0,abs(intValy)+1)
                pwm.channels[BL2_PWM].duty_cycle = abs(intValy)

            else:

                pwm.channels[BL1_PWM].duty_cycle = 0 
                pwm.channels[BL2_PWM].duty_cycle = 0
                    
                    #this block controls the vertical thrusters
            if intValrx>100:
            
                GPIO.output(OR1,GPIO.LOW)#direction pin
                GPIO.output(BR1,GPIO.LOW)#direction pin

        

                #pwm.setPWM(OR1_PWM,0,abs(intValrx)+1)
                pwm.channels[OR1_PWM].duty_cycle = abs(intValrx)
                #pwm.setPWM(BR1_PWM,0,abs(intValrx)+1)
               
                
                pwm.channels[BR1_PWM].duty_cycle = abs(intValrx)



            elif intValry>100:
            
                GPIO.output(OR1,GPIO.HIGH)#direction pin
 
                GPIO.output(BR1,GPIO.HIGH)#direction pin
   
                pwm.channels[OR1_PWM].duty_cycle = abs(intValry)
                pwm.channels[BR1_PWM].duty_cycle = abs(intValry)
            else:

                pwm.channels[OR1_PWM].duty_cycle = 0
                pwm.channels[BR1_PWM].duty_cycle = 0
                

            
            
except KeyboardInterrupt:            
    GPIO.cleanup()
    # Clear display.
    oled.fill(0)
    oled.show()
