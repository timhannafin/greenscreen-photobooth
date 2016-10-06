import time
from Tkinter import *
import picamera
import pygame
from backgroundgallery import *
from SimpleCV import *
import numpy as np
import shutil
import facebook
import ConfigParser
import cv2

camera = picamera.PiCamera()
camera.awb_mode = 'off'




configFileName = "settings.cfg"
config = ConfigParser.ConfigParser()
config.read(configFileName)

camera.awb_gains = (config.getfloat("camera","red_balance"), config.getfloat("camera","blue_balance"))
time.sleep(2)


MAX_HUE = config.getint("chromakey","max_hue") + config.getint("chromakey","max_hue_tolerance")
MIN_HUE = config.getint("chromakey","min_hue") - config.getint("chromakey","min_hue_tolerance")



countdownLength = 5;


DISPLAY_WIDTH = config.getint("photo_resolution","display_width")
DISPLAY_HEIGHT = config.getint("photo_resolution","display_height")
SAVE_HEIGHT = config.getint("photo_resolution","save_height")
SAVE_WIDTH = config.getint("photo_resolution","save_width")
RAW_FILENAME = config.get("photo_resolution","temp_filename")

SCALE = 1.8
PROGRAM_STATE = None

def captureImageInputEvent(event):
    if PROGRAM_STATE == "READY":
        captureImage()
    elif PROGRAM_STATE == "REVIEW":
        selectBackground()
    elif PROGRAM_STATE == "FINAL PREVIEW":
        savePhoto()
    else:
        return
    
def backInputEvent(event):
    if PROGRAM_STATE == "REVIEW":
        returnToInitialState()
    elif PROGRAM_STATE == "FINAL PREVIEW":
        selectBackground()
    elif PROGRAM_STATE == "BACKGROUND":
        previewImage()
    return

def galleryClickCallback(filepath):
    applyBackground(filepath)
    previewFinal()
    return

def close(event):
    camera.stop_preview()
    root.withdraw()
    sys.exit(1)
    return

def clearCanvas():
    #print "cleared"
    can.delete("all")
    for child in can.winfo_children():     
        child.destroy() 
    can.pack_forget()
    can.pack(fill=BOTH, expand=1)
    return

def setProgramState(state):
    global PROGRAM_STATE
    PROGRAM_STATE = state
    #print PROGRAM_STATE
    return

def setInfoLabel(info):
    infoLabel.config(state=NORMAL)
    infoLabel.delete(1.0, "end")

    gIndex=None
    while info.find("<GREEN>") > -1:
        gIndex = info.find("<GREEN>")
        info = info.replace("<GREEN>", u"\u2B24")
    

    rIndex=None
    while info.find("<RED>") > -1:
        rIndex = info.find("<RED>")
        info = info.replace("<RED>", u"\u2B24")
    infoLabel.insert(INSERT, info)
    
    if gIndex != None:
        infoLabel.tag_add("green", "1.%d"%gIndex, "1.%d"%(gIndex+1))

    if rIndex != None:
        infoLabel.tag_add("red", "1.%d"%rIndex, "1.%d"%(rIndex+1))
          
    infoLabel.tag_add("center", 1.0, "end")
    infoLabel.config(state=DISABLED)
    return

def applyBackground(backgroundFilepath):
    raw_image = cv2.imread(RAW_FILENAME)
    background = cv2.imread(backgroundFilepath)

    hsv_raw = cv2.cvtColor(raw_image, cv2.COLOR_BGR2HSV)
    lowerBound = np.array([MIN_HUE,0,0], np.uint8)
    upperBound = np.array([MAX_HUE,255,255], np.uint8)
    mask = cv2.inRange(hsv_raw,lowerBound,upperBound)
    inv_mask = cv2.bitwise_not(mask)
    masked_img = cv2.bitwise_and(raw_image,raw_image,mask=inv_mask)
    masked_background = cv2.bitwise_and(background,background,mask=mask)
    output_img = cv2.bitwise_or(masked_img,masked_background)
    cv2.imwrite("screened.jpg",output_img)
    return

def previewFinal():
    clearCanvas()
    setProgramState("FINAL PREVIEW")
    setInfoLabel("<GREEN>-Save       <RED>-Go Back")
    finalImg = Image("screened.jpg")
    finalImg = finalImg.resize(can.winfo_width(),can.winfo_height());    
    image_tk = ImageTk.PhotoImage(finalImg.getPIL())
    can.copy_image = image_tk
    can.create_image([0,0],anchor=NW,image=can.copy_image,tags="image")
    can.pack()

def previewImage():
    clearCanvas()
    setInfoLabel("<GREEN>-OK       <RED>-Try Again")
    snapshot = Image(RAW_FILENAME)
    snapshot = snapshot.resize(can.winfo_width(),can.winfo_height());    
    image_tk = ImageTk.PhotoImage(snapshot.getPIL())
    can.copy_image = image_tk
    can.create_image([0,0],anchor=NW,image=can.copy_image,tags="image")
    can.pack()
    setProgramState("REVIEW")
    
def selectBackground():
    clearCanvas()
    setProgramState("BACKGROUND")
    setInfoLabel("Touch screen to select your background")
    gallery = BackgroundGallery("/home/pi/backgrounds/")
    galleryFrame = Frame(can)
    gallery.drawGalleryFrame(galleryFrame, can.winfo_width(), galleryClickCallback)
    galleryFrame.pack(fill=BOTH, expand=1)
    
    return

    
def captureImage():
    setProgramState("CAPTURING")
    displayCountdown()
    camera.capture(RAW_FILENAME, resize=(SAVE_WIDTH, SAVE_HEIGHT))
    camera.stop_preview()
    previewImage()
    
def displayCountdown():
    camera.preview_alpha = 128
    for i in range(countdownLength):
        can.delete("text")
        can.update()
        can.create_text(can.winfo_width()/2, (can.winfo_height()/2)-10, fill="White",font=('Arial', can.winfo_height()-10), text=str(countdownLength - i), tags="text")
        can.update()
        if i < countdownLength - 2:
            time.sleep(1)
        else:
            for j in range(5):
                time.sleep(.2)
    can.delete("text")
    return

def returnToInitialState():
    clearCanvas()
    camera.start_preview()
    setInfoLabel("Smile!")
    setProgramState("READY")
    return

def editPhoto():
    return

def savePhoto():
    setProgramState("SAVE")
    if config.get("facebook", "facebook_upload") == "true":
        facebookUpload()
    shutil.copy2("screened.jpg", "saved_photos/%d.jpg"%time.time())
    shutil.copy2("snapshot.jpg", "raw_images/%d.jpg"%time.time())
    returnToInitialState()
    return

def facebookUpload():
    access_token=config.get("facebook","facebook_api_key")
    user = config.get("facebook","facebook_user")
    graph = facebook.GraphAPI(access_token, version="2.7", timeout=30)
    album_id = "/%s/photos" % config.get("facebook","facebook_album_id")
    print album_id
    message = config.get("facebook","facebook_default_caption")
    graph.put_photo(image=open("screened.jpg", 'rb'), message=message, album_path=album_id)
    return


root = Tk()
root.attributes("-fullscreen",True)
root.config(cursor="none")

w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.update()

infoLabel = Text(root, state=DISABLED, height=1, font=("Arial", 18), bd=0)
infoLabel.tag_configure("center", justify="center")
infoLabel.tag_configure("green", foreground="#00FF00")
infoLabel.tag_configure("red", foreground="#FF0000")
setInfoLabel("Smile!")


infoLabel.pack(fill=X, side=BOTTOM)

can = Canvas(root, highlightthickness=0, bg="#000000")
can.pack(fill=BOTH, expand=1, side=BOTTOM)
root.bind('<space>',captureImageInputEvent)
root.bind('<Escape>',close)
root.bind('s',backInputEvent)

root.wm_title("Tim's Photobooth")
camera.start_preview()
setProgramState("READY")
root.mainloop()





