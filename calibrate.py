import cv2
import numpy as np
import picamera
import time
import ConfigParser


configFileName = "settings.cfg"
config = ConfigParser.ConfigParser()
config.read(configFileName)


camera = picamera.PiCamera()
camera.awb_mode = 'auto'
print "Preparing to calibrate green screen"
print "Move the camera and screen until the entire frame is filled with the screen. Then press enter."
raw_input("Press enter to continue")
camera.start_preview()
raw_input("")
camera.stop_preview()

print "Configuring white balance. Hold a white object like a piece of paper in front of the screen and then press enter."
raw_input("Press enter to continue...")
camera.start_preview()
raw_input("")
time.sleep(2)
print "Getting white balance"
config.set("camera","red_balance",str(float(camera.awb_gains[0])))
config.set("camera","blue_balance",str(float(camera.awb_gains[1])))
camera.awb_mode = 'off'
red = config.getfloat("camera","red_balance")
blue = config.getfloat("camera","blue_balance")
camera.awb_gains = (red, blue)
camera.stop_preview()
print "Red balance: %s" % red
print "Blue balance: %s" % blue

print "Configuring chroma key values. Make sure the camera can see only the backdrop. Then press enter."
raw_input("Press enter to continue")
camera.start_preview()
raw_input("")
camera.stop_preview()
camera.capture("calibration.jpg", resize=(1024,768))
screen = cv2.imread("calibration.jpg")


hsv_screen = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)

hueMax = hsv_screen[:,:,0].max()
hueMin = hsv_screen[:,:,0].min()

print "Hue range %s - %s" % (hueMin, hueMax)
config.set("chromakey","max_hue",hueMax)
config.set("chromakey","min_hue",hueMin)

lowerBound = np.array([hueMin,0,0], np.uint8)
upperBound = np.array([hueMax,255,255], np.uint8)

configFile = open(configFileName, 'w')
config.write(configFile)
configFile.close()
