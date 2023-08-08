		    #Assign temp values to divide the x and y axes into left and right, up and down		
		    tempY = (4094-abs(fValx2)) * (fValy2/4094) + fValy2
		    tempX = (4094-abs(fValy2)) * (fValx2/4094) + fValx2	
			#Now divide into right side and left side
		    RIGHT = int(tempY + tempX)/2
		    LEFT = int(tempY - tempX)/2
			
		    if fValy2<-100 & (100<fValx2<-100):
			
				GPIO.output(BL1,GPIO.LOW)#direction pin
				GPIO.output(GR1,GPIO.LOW)#direction pin
				
		    elif fValy2>100 & (100<fValx2<-100):
			
				GPIO.output(BL1,GPIO.HIGH)#direction pin
			    GPIO.output(GR1,GPIO.HIGH)#direction pin
			else:
			
				GPIO.output(6,GPIO.HIGH)#Turn on LED


		    if fValx2<-100 & (-100<fValy2<100):
			
				GPIO.output(BL1,GPIO.HIGH)#direction pin
				GPIO.output(GR1,GPIO.LOW)#direction pin

             elif fValx2>100 & (-100<fValy2<100):
			
				GPIO.output(BL1,GPIO.LOW)#direction pin
				GPIO.output(GR1,GPIO.HIGH)#direction pin

				
		    else:
	        	GPIO.output(16,GPIO.HIGH)#Turn on other LED			

		    if intValy>100:
			
				GPIO.output(OR1,GPIO.LOW)#direction pin
				
				
		    elseif intValy<-100:
			
				GPIO.output(OR1,GPIO.HIGH)#direction pin

			else:
				GPIO.output(6,GPIO.LOW)#Turn off LED
				GPIO.output(16,GPIO.LOW)#Turn off LED
				

				
			
		    print "%s  %s: %d" % (axis, "right",RIGHT)	
		    print "%s  %s: %d" % (axis, "left",LEFT)
		
			
		    pwm.setPWM(BL1_PWM,1,abs(LEFT)+1)
		    pwm.setPWM(GR1_PWM,1,abs(RIGHT)+1)
		    pwm.setPWM(OR1_PWM,1,abs(intValy)+1)
