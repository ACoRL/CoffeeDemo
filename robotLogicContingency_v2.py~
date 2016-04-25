import cv2
import freenect
import numpy as np
import skimage.measure
import sys
import numpy
import os
import serial
import time
from PIL import Image
from skimage import color
from LBAR_Class import LBAR

size = 300,230

print(sys.argv)

DEBUGGING = True

print("Connecting")
lbar = LBAR("/dev/rfcomm0", 9600)
print("Created object")
time.sleep(3)
print("Connected")

print("Done now, GOOOOO")


static_frame,_ = freenect.sync_get_video()

#scale down current frame
#static_frame = cv2.pyrDown(static_frame, (50,50))


# Direction Constants
STRAIGHT = 0
LEFT     = 7
RIGHT    = 1

DIRECTIONS = (STRAIGHT, LEFT, RIGHT)

TURN_INDICATOR = {1 :LEFT,  3 :LEFT,  5 :RIGHT,
                  7 :RIGHT, 9 :RIGHT, 11:LEFT,
                  13:LEFT,  15:RIGHT, 17:RIGHT}

DIRECTION_IMAGES = [
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]}, {'0':[], '1':[], '7':[]},
    {'0':[], '1':[], '7':[]},
]

def driveForward():
    lbar.send(1)
    
    

def driveLeft():
    lbar.send(7)
    time.sleep(.5)
    
    

def driveRight():
    lbar.send(9)
    time.sleep(.5)
    
    
    
def turnLeft():
    lbar.send(5)
    time.sleep(.5)
    
    
    
def turnRight():
    lbar.send(6)
    time.sleep(.5)
    
    

def keywithmaxval(d): # Stack Overflow : the wolf
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]
     


def compare_imgs(curr_frame, end_frame):
    '''
    Return a value which represents how similar
    one image is to another from 0 to 1.
        0 represents completely dissimilar,
        1 represents the same image
    '''
    #curr_frame = calc_hist(curr_frame)
    #end_frame = calc_hist(end_frame)
    #h1 = np.histogramdd(curr_frame)
    #h2 = np.histogramdd(end_frame)
    #print(curr_frame)
    
    
    return skimage.measure.structural_similarity(curr_frame, end_frame)
    #return cv2.compareHist(curr_frame, end_frame)
    #val = mse(curr_frame, end_frame)
    #d = cv2.compareHist(np_hist_to_cv(h1), np_hist_to_cv(h2),
    #                cv2.cv.CV_COMP_BHATTACHARYYA)
    #return d


def init_images():
    '''
    Get all the images for a given state and direction 
    FROM THE something lol and return it inside an array.
    '''
    
    for state in range(1):
        for direction in ['0', '1', '7']:
            if DEBUGGING:
                print("Loading images for state " + str(state) + " and direction " + direction)
            _dir = "/home/acorl/Desktop/coffee_demo/rgb_frames/" + str(state) + "/" + str(direction) + "/"
            if DEBUGGING:
                count = 0
            for filename in os.listdir(_dir):
                if DEBUGGING:
                    count += 1
                DIRECTION_IMAGES[state][direction].append(color.rgb2gray(cv2.imread(_dir + filename)))
            if DEBUGGING:
                print("Loaded " + str(count) + " images.")


def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
	
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def np_hist_to_cv(np_histogram_output):
    counts, bin_edges = np_histogram_output
    return counts.ravel().astype('float32')

def calc_hist(img):
    return cv2.calcHist([img],[0],None,[256],[0,256])

def get_direction_images(state, direction):
    return DIRECTION_IMAGES[state][str(direction)]


def get_final_state_image(state, direction=0):
    '''
    Get the last image for the given state
    or get the first image for the next state
    '''
    return get_direction_images(state, direction)[-1]



def transition_reached(curr_frame, final_state_image, confidence_threshold=.7):
    '''Check for state changes'''
    conf = compare_imgs(curr_frame, final_state_image)
    return conf >= confidence_threshold
    



def get_direction(curr_frame, state):
    '''Determine which direction the current frame is most likely pointing'''
    direc_possibilities = {0:0, 1:0, 7:0}
    for direction in DIRECTIONS:
        if DEBUGGING:
            print("Checking images for direction:" + str(direction))
        img_directions = get_direction_images(state, direction)
        for img in img_directions:
            if transition_reached(curr_frame, img):
                direc_possibilities[direction] += 1
    print(direc_possibilities)
    return keywithmaxval(direc_possibilities)



def rotate(direction):
    '''Direction is an integer, value given by the constants'''
    if direction == LEFT:
        turnLeft()
    else:
        turnRight()



def navigate(direction):
    '''
    Sends the commands to go straight or to correct the
    course in case the robot gets off-center.
    '''
    #similar = compare_imgs(curr_frame, final_state_image)
    if DEBUGGING:
        print("Have NOT reached a state change")
        
    if direction == STRAIGHT:
        if DEBUGGING:
            print("Drive straight.")
        driveForward()
    elif direction == LEFT:
        if DEBUGGING:
            print("Looking left, drive right")
        driveRight()
    elif direction == RIGHT:
        if DEBUGGING:
            print("Looking right, drive left")
        driveLeft()
    else:
        #freak out mode engaged
        if DEBUGGING:
            print("I don't know where to drive.")
        turnLeft()
        pass

#from skimage.viewer import ImageViewer
def main():
    prevgray,_ = freenect.sync_get_video()
    prevgray = cv2.cvtColor(prevgray, cv2.COLOR_BGR2GRAY)
    prevgray = cv2.resize(prevgray, (200, 200))
    
    while True:
        gray,_ = freenect.sync_get_video()
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (200, 200))
        
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        prevgray = gray
        
        step = 16
        
        h, w = gray.shape[:2]
        y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(int)
        fx, fy = flow[y,x].T
        
        fx_avg = np.average(fx)
        
        if ((fx_avg > 0)):
        
            print('Moved left')
            #driveRight()
            
        elif ((fx_avg < 0)):
        
            print('Moved right')
            #driveLeft()
            
        else:
            print('Looking straight')
            #driveForward()
            
if __name__ == "__main__":
    main()
