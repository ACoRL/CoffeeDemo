from __future__ import print_function
import os,cv2
from PIL import Image
_dir = "/home/acorl/Desktop/coffee_demo/rgb_frames/imgs"

size = 300,230

hello = "HELLOOOOOO"

for file in os.listdir(_dir):
        print(file, end='    :    ')
        print(file.split("_")[0])
        #img = cv2.imread(_dir + "/" + file,0)
        im = Image.open(_dir + "/" + file)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(_dir + "/../" + file.split("_")[0] + "/" + file.split("_")[-1][0] + "/" + file, "PNG")
        #cv2.imshow("Show", img)
        #img_dst = img
        
        #img = cv2.pyrDown(img, (.001,.001))
        
        #cv2.imwrite(_dir + "/../" + file.split("_")[0] + "/" + file.split("_")[-1][0] + "/" + file,img)
 
        
        

