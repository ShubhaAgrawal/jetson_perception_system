# save this as /tmp/led_test.py
import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(15, GPIO.OUT, initial=GPIO.LOW)   # blue
GPIO.setup(33, GPIO.OUT, initial=GPIO.LOW)   # green
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW)   # red
GPIO.setup(7, GPIO.OUT)
    
print("Blue on")
GPIO.output(15, GPIO.HIGH)
time.sleep(2)
GPIO.output(15, GPIO.LOW)

print("Green on")
GPIO.output(33, GPIO.HIGH)
time.sleep(2)
GPIO.output(33, GPIO.LOW)

print("Red on")
GPIO.output(29, GPIO.HIGH)
time.sleep(2)
GPIO.output(29, GPIO.LOW)

GPIO.cleanup()
print("Done")