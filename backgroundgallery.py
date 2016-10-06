from Tkinter import *
import glob
import ImageTk
from PIL import Image


class GalleryItem:
    image = None
    filepath = None
    def __init__(self, filepath):
        self.image = Image.open(filepath)
        self.filepath = filepath


    
class BackgroundGallery:
    filelist = []
    objectList = []
    def __init__(self, directory):
        self.filelist = []
        self.objectList = []        
        extensions = ("*.png","*.jpg","*.jpeg")
        for extension in extensions:
            self.filelist.extend(glob.glob(directory + extension))

        for filename in self.filelist:
            self.objectList.append( GalleryItem(filename) )
        return

    def getGUIObjects(self):

        return objectList

    def drawGalleryFrame(self, galleryFrame, width, callback):     

        cell_width = width/4
        
        can = Canvas(galleryFrame, highlightthickness=0,width=cell_width, height=(int)(cell_width * .75))
        can.grid(row=0,column=0)
        can.update()
        can.create_text([can.winfo_width()/2, can.winfo_height()/2], text="None")

        callback_func = lambda filepath: ( lambda x: callback(filepath))
        can.bind('<Button-1>',callback_func(None))
        
        c=1
        r=0
        for img in self.objectList:
            img.image = img.image.resize((cell_width, (int)(cell_width * .75)))
            can = Canvas(galleryFrame, bg="#000000", highlightthickness=0,width=cell_width, height=(int)(cell_width * .75))
            can.copy_image = ImageTk.PhotoImage(img.image)            
            can.grid(row=r,column=c)
            can.create_image([0,0],anchor=NW,image = can.copy_image, tags="image")

            
            can.bind('<Button-1>',callback_func(img.filepath))
            c = c+1

            if c%4 == 0:
                c=0
                r=r+1
            
        #galleryFrame.pack(fill=BOTH, expand=1)
        return galleryFrame

    def getFilelist(self):
        return self.filelist
        return

def galleryClickCallback(filename):
    print filename
    return




