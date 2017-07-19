from Adafruit_PWM_Servo_Driver import PWM
import time

pwm = PWM(0x40)
pwm.setPWMFreq(50)
pwm.setPWM(0,0,306)
pwm.setPWM(1,0,306)