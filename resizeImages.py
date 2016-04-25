from __future__ import print_function
import os,cv2
from PIL import Image
_dir = "/home/acorl/Desktop/coffee_demo/rgb_frames/imgs"

size = 300,230

'''
All this program does is take all the images from
the coffee_demo/rgb_frame/imgs directory,
resize all of them using whatever method we choose
and applying whatever operations we want as well,
then to sort all of them into the correct
state and direction folder.
'''

for file in os.listdir(_dir):
        print(file, end='    :    ')
        print(file.split("_")[0])
        # Image resize using PIL
        #im = Image.open(_dir + "/" + file)
        #im.thumbnail(size, Image.ANTIALIAS)
        #im.save(_dir + "/../" + file.split("_")[0] + "/" + file.split("_")[-1][0] + "/" + file, "PNG")         #cv2.imshow("Show", img)
        
        # Image resize using OpenCV
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cv2.resize(img, size)
        
        img = cv2.imread(_dir + "/" + file,0)
        img_dst = img
        
        img = cv2.pyrDown(img, (.001,.001))
        
        # Save the image in the directory containing the imgs folder in a
        # folder named after the state and a folder named after the  direction
        # Both of which are specified in the file name of the image opened.
        cv2.imwrite(_dir + "/../" + file.split("_")[0] + "/" + file.split("_")[-1][0] + "/" + file,img)
