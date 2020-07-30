import threading
import time
import math
import board
import busio
#import adafruit_bno055
import adafruit_fxos8700
import adafruit_fxas21002c
import adafruit_ssd1306
import adafruit_pca9685
import adafruit_bme280
from PIL import Image, ImageDraw, ImageFont
import serial

import math
import time
import os, sys, struct, array
from fcntl import ioctl
import RPi.GPIO as GPIO

import subprocess
#I2C address for the IMU is 0x28
#i2c_bno = board.I2C()
#sensor = adafruit_bno055.BNO055_I2C(i2c_bno,0x28)

i2c_nxp = board.I2C()
mag_accel_sensor = adafruit_fxos8700.FXOS8700(i2c_nxp)
gyro_sensor = adafruit_fxas21002c.FXAS21002C(i2c_nxp)

#I2C address for the OLED screen is 0x3c
i2c_oled = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128,64, i2c_oled,addr=0x3c,reset=[])

#I2C address for the temp, humidity and pressure sensor is 0x76
i2c_bme = board.I2C()
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c_bme,0x76)

def sensor_read(arg1):
    while True:
        global yaw
        global pitch
        global roll
        
        global yawDeg
        global yawE
        global pitchDeg
        global rollDeg
        
        #take 10 readings per second
        time.sleep(0.1)
        try:
         #Read IMU
            mag_x, mag_y, mag_z = mag_accel_sensor.magnetometer
            accel_x, accel_y, accel_z = mag_accel_sensor.accelerometer
            gyro_x, gyro_y, gyro_z = gyro_sensor.gyroscope
                  
            #We use print statements for debugging - comment out to spee execution
            #print("mag: {},{},{}".format(mag_x, mag_y, mag_z))
            #print("accel: {}".format(mag_accel_sensor.accelerometer))
              
            pitch = math.atan2(accel_x,math.sqrt(accel_y**2+accel_z**2))
            roll = math.atan2(accel_y,math.sqrt(accel_x**2+accel_z**2))
            #pitch = math.atan2(-accel_x,math.sqrt(accel_y**2+accel_z**2))
            #roll = math.atan2(accel_y,accel_z)
            mag_cal_x = -1.25
            mag_cal_y = -44.9
            mag_cal_z = -84.7
            
            mag_x = mag_x-mag_cal_x
            mag_y = mag_y-mag_cal_y
            mag_z = mag_z-mag_cal_z
            
            
            yaw = math.atan2(mag_y,mag_x)
            if yaw < 0:
                yaw=yaw+2*math.pi

            #tilt compensation
            x_h = mag_x*math.cos(pitch) + mag_z*math.sin(pitch)
            y_h = mag_x*math.sin(roll)*math.sin(pitch)+mag_y*math.cos(roll)-mag_z*math.sin(roll)*math.cos(pitch)
            
            tilt_yaw = math.atan2(y_h,x_h)
            
            if tilt_yaw < 0:
                tilt_yaw=tilt_yaw+2*math.pi
                
                
        except:

            subprocess.call(['i2cdetect', '-y', '1'])
            continue
        
        yawTilt = tilt_yaw*57.2958
        #convert radians to degrees
        rollDeg = roll*57.2958
        pitchDeg = pitch*57.2958
        yawDeg = yaw*57.2958
            
        print("Yaw: {}".format(yawTilt))
        print("Yaw2: {}".format(yawDeg))
        
        
        #print("Pitch: {}".format(sensor.euler[1]))
        #print("Pitch2: {}".format(pitchDeg))
        #print("cal: {}".format(sensor.calibration_status))
        xx = round(math.cos(tilt_yaw-math.pi/2)*23)
        yy = round(math.sin(tilt_yaw-math.pi/2)*23)
        
        image = Image.new("1",(128,64))
        draw = ImageDraw.Draw(image)
        
        font = ImageFont.load_default()

        draw.ellipse((41,17,87,63),outline=255, fill=0)#left,top,right,bottom
             
        draw.line((xx+64,yy+41,64,41),fill=255) #[left (beginning), top] head, [right (end), bottom] tail - tail is always at center

        draw.text((0,-2),"Yaw: {}".format(round(yawTilt)),font=font,fill=255)
        draw.text((64,-2),"Pitch: {}".format(round(pitchDeg)),font=font,fill=255)
        draw.text((0,6),"Roll: {}".format(round(rollDeg)),font=font,fill=255)

        draw.text((0,14),"T: {:0.1f}C".format((bme280.temperature)),font=font,fill=255)
        draw.text((0,22),"H: {}%".format(round(bme280.humidity)),font=font,fill=255)
        draw.text((64,6),"P: {}mbar".format(round(bme280.pressure)),font=font,fill=255)

        oled.image(image)
        oled.show()
        
t = threading.Thread(target=sensor_read,args=(1,),daemon=True).start()

# Setup OLED screen - get parameters
width = oled.width
height = oled.height
image = Image.new('1', (width, height))

font = ImageFont.load_default()
try:
    while True:
        pass
 
except (KeyboardInterrupt,SystemExit):
    print("out")

