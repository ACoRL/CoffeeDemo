import cv2
import freenect
import skimage.measure
import serial
import time
#from PIL import Image
from skimage import color
from LBAR_Class import LBAR

# Image resizing size
size = 300,230

conf = float(sys.argv[-1])

DEBUGGING = True

# Connect to bluetooth
if DEBUGGING:
    print("Connecting")
lbar = LBAR("/dev/rfcomm0", 9600)
if DEBUGGING:
    print("Created object")
time.sleep(3)
if DEBUGGING:
    print("Connected")

print("Done now, GOOOOO")


static_frame,_ = freenect.sync_get_video()

# Direction Constants
STRAIGHT = 0
LEFT     = 7
RIGHT    = 1

DIRECTIONS = [STRAIGHT, LEFT, RIGHT]

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
     """ a) Create a list of the dict's keys and values; 
         b) Return the key with the max value"""  
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
    return skimage.measure.structural_similarity(curr_frame, end_frame)

def init_images():
    '''
    Get all the images for a given state and direction 
    FROM THE something lol and return it inside an array.
    '''
    for state in range(1):
        for direction in map(str, DIRECTIONS):
            if DEBUGGING:
                print("Loading images for state " + str(state)
                      + " and direction " + direction)
            _dir = "/home/acorl/Desktop/coffee_demo/rgb_frames/"
                   + str(state) + "/" + str(direction) + "/"
            
            # Loading grayscale images in the correct state and direction
            for filename in os.listdir(_dir):
                DIRECTION_IMAGES[state][direction].append(color.rgb2gray(cv2.imread(_dir + filename)))

def get_direction_images(state, direction):
    return DIRECTION_IMAGES[state][str(direction)]

def get_final_state_image(state, direction=0):
    '''
    Get the last image for the given state by
    getting the last image in the array
    (This assumes the images are ordered)
    '''
    return get_direction_images(state, direction)[-1]

def similar_enough(curr_frame, final_state_image, confidence_threshold=.7):
    '''Returns True if the curr_frame is similar enough to final_state_image, otherwise...'''
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
            if similar_enough(curr_frame, img):
                direc_possibilities[direction] += 1
                
    if DEBUGGING:
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
        # Freak out mode engaged
        if DEBUGGING:
            print("I don't know where to drive.")
        turnLeft()
        pass

def main():
    # The range where we allow before we consider 
    # movement left or right.
    # Note, look at a normal distribution, we're
    # talking about allowing a range for how much
    # movement we allowing before we we start
    # to say whether there was movement to the
    # left or to the right.
    alpha = 0
    
    # Get previous image, resize it, convert it to grayscale.
    prevgray,_ = freenect.sync_get_video()
    prevgray = cv2.cvtColor(prevgray, cv2.COLOR_BGR2GRAY)
    prevgray = cv2.resize(prevgray, size)
    
    while True:
        # Get new image, resize it, convert it to grayscale.
        gray,_ = freenect.sync_get_video()
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, size)
        
        # Calculate the optical flow using this handy built in method.
        flow = cv2.calcOpticalFlowFarneback(prevgray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        
        # Set the newly gathered image to the previous one.
        prevgray = gray
        
        # Set the steps for do.
        step = 16
        
        # Draw the dots and lines on the screen.
        h, w = gray.shape[:2]
        y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2, -1).astype(int)
        fx, fy = flow[y,x].T
        
        # Get the average amount of displacement within the screen
        # with positive being left and negative being right.
        fx_avg = np.average(fx)
        
        # Keep it straight!
        if ((fx_avg > alpha)):
            print('Moved right')
            #driveLeft()
        elif ((fx_avg < -alpha)):
            print('Moved left')
            #driveRight()
        else:
            print('Looking straight')
            #driveForward()
            
if __name__ == "__main__":
    main()
