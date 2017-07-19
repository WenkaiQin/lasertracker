#!/usr/bin/python
from picamera import PiCamera
from Adafruit_PWM_Servo_Driver import PWM
import time

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
pwm = PWM(0x40)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)

delay = 1
servoMin1 = 400  # Min pulse length out of 4096
servoMax1 = 500  # Max pulse length out of 4096
servoMin2 = 300  # Min pulse length out of 4096
servoMax2 = 400  # Max pulse length out of 4096
servoRest1 = (servoMin1+servoMax1)/2
servoRest2 = (servoMin2+servoMax2)/2

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
camera = PiCamera()
camera.start_preview()
while (True):
  pwm.setPWM(0,0,servoMin1)
  pwm.setPWM(1,0,servoMin2)
  time.sleep(delay)
  
  pwm.setPWM(0,0,servoMax1)
  pwm.setPWM(1,0,servoMin2)
  time.sleep(delay)

  pwm.setPWM(0,0,servoMin1)
  pwm.setPWM(1,0,servoMax2)
  time.sleep(delay)

  pwm.setPWM(0,0,servoMax1)
  pwm.setPWM(1,0,servoMax2)
  time.sleep(delay)

